"""
ARIA Deep Repository Context Engine.
Performs AST-level repo tree ingestion, relevant file retrieval (Repo RAG),
and snippet extraction to give ARIA complete context of the target codebase.
"""

import os
import re
import json
import base64
import logging
import subprocess
from typing import List, Dict, Any, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class RepoContextFetcher:
    """
    Ingests remote repository directory trees and retrieves targeted file context
    using the GitHub CLI (gh api).
    """

    TIMEOUT_SECONDS = 15

    IGNORED_DIRS: Set[str] = {
        "node_modules",
        ".git",
        ".github",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        "out",
        "target",
        ".next",
        ".turbo",
        ".yarn",
        "coverage",
        ".cache",
        "tmp",
        "temp",
        ".idea",
        ".vscode",
    }

    IGNORED_EXTENSIONS: Set[str] = {
        # Images & Media
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp", ".tiff", ".psd",
        ".mp3", ".mp4", ".wav", ".ogg", ".mov", ".avi", ".flv", ".m4a",
        # Binaries & Compiled
        ".exe", ".dll", ".so", ".dylib", ".bin", ".obj", ".o", ".a", ".lib",
        ".pyc", ".pyo", ".pyd", ".class", ".jar", ".war",
        # Fonts
        ".ttf", ".woff", ".woff2", ".eot", ".otf",
        # Archives
        ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar",
        # Documents & Binary Data
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # Source maps & minified files
        ".map", ".min.js", ".min.css",
        # Lock files
        ".lock",
    }

    IGNORED_FILES: Set[str] = {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "poetry.lock",
        "pipfile.lock",
        "gemfile.lock",
        "composer.lock",
        "cargo.lock",
        ".ds_store",
        "thumbs.db",
        ".gitignore",
        ".gitattributes",
        ".dockerignore",
    }

    CODE_EXTENSIONS: Set[str] = {
        ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java",
        ".c", ".cpp", ".cc", ".h", ".hpp", ".rb", ".php", ".cs",
        ".swift", ".kt", ".scala", ".vue", ".svelte",
    }

    STOP_WORDS: Set[str] = {
        "the", "and", "for", "with", "that", "this", "from", "have", "not",
        "are", "you", "which", "will", "can", "when", "into", "more", "then",
        "them", "some", "what", "also", "here", "just", "like", "make", "only",
        "such", "than", "been", "call", "does", "each", "even", "find", "give",
        "help", "many", "most", "must", "name", "same", "take", "there", "these",
        "they", "thing", "time", "very", "were", "while", "who", "would", "your",
        "issue", "error", "fixed", "fixing", "problem", "fails", "failed", "bug",
    }

    def __init__(self):
        self._tree_cache: Dict[str, List[str]] = {}

    def get_repo_tree(self, repo: str, force_refresh: bool = False) -> List[str]:
        """
        Runs `gh api repos/{repo}/git/trees/main?recursive=1` (or fallback to `master`)
        to get all file paths in the repo. Filters out non-code assets.
        """
        if not repo or "/" not in repo:
            return []

        if not force_refresh and repo in self._tree_cache:
            return self._tree_cache[repo]

        branches = ["main", "master", "HEAD"]
        raw_items: List[Dict[str, Any]] = []

        for branch in branches:
            cmd = ["gh", "api", f"repos/{repo}/git/trees/{branch}?recursive=1"]
            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SECONDS,
                )
                if res.returncode == 0 and res.stdout:
                    data = json.loads(res.stdout)
                    tree = data.get("tree")
                    if isinstance(tree, list) and tree:
                        raw_items = tree
                        break
            except Exception as exc:
                logger.debug("Failed tree fetch for %s branch %s: %s", repo, branch, exc)

        if not raw_items:
            logger.warning("Could not retrieve repository tree for %s", repo)
            return []

        filtered_paths: List[str] = []
        for item in raw_items:
            if item.get("type") != "blob":
                continue

            path = item.get("path", "")
            if not path:
                continue

            parts = set(path.lower().split("/"))
            if parts & self.IGNORED_DIRS:
                continue

            filename = path.rsplit("/", 1)[-1].lower()
            if filename in self.IGNORED_FILES:
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext in self.IGNORED_EXTENSIONS:
                continue

            filtered_paths.append(path)

        self._tree_cache[repo] = filtered_paths
        return filtered_paths

    def find_relevant_files(
        self,
        repo: str,
        issue_title: str,
        issue_body: str,
        max_files: int = 3,
        tree: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Scans tree for file paths explicitly mentioned in the issue title/body
        and scores paths against keywords in issue title/body.
        Returns top `max_files` most relevant file paths.
        """
        tree_paths = tree if tree is not None else self.get_repo_tree(repo)
        if not tree_paths:
            return []

        scored = self._score_tree_files(tree_paths, issue_title, issue_body)
        return [p for p, _ in scored[:max_files]]

    def _score_tree_files(
        self,
        tree_paths: List[str],
        issue_title: str,
        issue_body: str,
    ) -> List[Tuple[str, float]]:
        """
        Scores files in tree against explicit mentions and keyword relevance.
        Returns list of (path, score) pairs sorted descending by score.
        """
        full_text = f"{issue_title}\n{issue_body}"

        # 1. Extract explicit candidate file paths / names mentioned in text
        explicit_candidates = self._extract_explicit_file_mentions(full_text)

        # 2. Extract alphanumeric keyword tokens from title and body (splitting on underscore/hyphen too)
        title_words = {
            w.lower()
            for w in re.findall(r"[a-zA-Z0-9]+", issue_title)
            if len(w) >= 3 and w.lower() not in self.STOP_WORDS
        }
        body_words = {
            w.lower()
            for w in re.findall(r"[a-zA-Z0-9]+", issue_body)
            if len(w) >= 3 and w.lower() not in self.STOP_WORDS
        }

        # Also preserve hyphenated and underscored compound terms from title
        for compound in re.findall(r"[a-zA-Z0-9]+[_\-][a-zA-Z0-9]+", issue_title):
            norm = compound.lower().replace("-", "_")
            title_words.add(norm)
            title_words.add(norm.replace("_", "-"))

        issue_mentions_test = any(
            t in issue_title.lower() for t in ["test", "spec", "mock", "assert"]
        )

        scored: List[Tuple[str, float]] = []

        for path in tree_paths:
            score = 0.0
            path_lower = path.lower()
            filename = path.rsplit("/", 1)[-1].lower()
            stem, ext = os.path.splitext(filename)

            # Explicit matches
            for cand in explicit_candidates:
                cand_lower = cand.lower()
                if cand_lower == path_lower:
                    score += 1000.0
                elif path_lower.endswith("/" + cand_lower) or path_lower.endswith(cand_lower):
                    score += 500.0
                elif cand_lower == filename:
                    score += 300.0

            # Substring occurrence in full text
            if len(path) > 4 and path_lower in full_text.lower():
                score += 400.0
            elif len(filename) > 4 and filename in full_text.lower():
                score += 150.0

            # Path & filename token matches
            path_tokens = set(re.findall(r"[a-zA-Z0-9]+", path_lower))
            filename_tokens = set(re.findall(r"[a-zA-Z0-9]+", stem))

            # Title keywords (higher weight)
            for kw in title_words:
                if kw in filename_tokens:
                    score += 30.0
                elif kw in path_tokens:
                    score += 15.0
                elif kw in path_lower:
                    score += 5.0

            # Body keywords
            for kw in body_words:
                if kw in filename_tokens:
                    score += 10.0
                elif kw in path_tokens:
                    score += 5.0
                elif kw in path_lower:
                    score += 2.0

            # Only add code extension bonus / test adjustments if the file has base relevance
            if score > 0:
                if ext in self.CODE_EXTENSIONS:
                    score += 5.0

                is_test_file = any(
                    t in path_lower for t in ["test", "spec", "__tests__", "mock"]
                )
                if is_test_file and not issue_mentions_test:
                    score -= 15.0

                scored.append((path, score))

        # Sort descending by score; prefer shorter paths as tie breaker
        scored.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
        return scored

    def _extract_explicit_file_mentions(self, text: str) -> Set[str]:
        """Extracts candidate file paths or file names directly mentioned in text."""
        candidates: Set[str] = set()

        # Matches backticked strings: `path/to/file.ts` or `file.py`
        backticks = re.findall(r"`([^`\n\r]+)`", text)
        for b in backticks:
            b_clean = b.strip()
            if "/" in b_clean or any(b_clean.endswith(ext) for ext in self.CODE_EXTENSIONS):
                candidates.add(b_clean)

        # Matches standard file paths: packages/foo/bar.ts or src/lib/test.py
        path_matches = re.findall(
            r"(?:[a-zA-Z0-9_\-.]+/)+[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9]+", text
        )
        for p in path_matches:
            candidates.add(p.strip())

        # Matches standalone file names with code extensions
        filename_matches = re.findall(
            r"\b[a-zA-Z0-9_\-]+\.(?:ts|tsx|js|jsx|py|go|rs|java|rb|php|c|cpp|h|json|yaml|yml)\b",
            text,
        )
        for f in filename_matches:
            candidates.add(f.strip())

        return candidates

    def fetch_file_content(self, repo: str, path: str, max_chars: int = 4000) -> str:
        """
        Runs `gh api repos/{repo}/contents/{path}` or
        `gh api -H "Accept: application/vnd.github.v3.raw" repos/{repo}/contents/{path}`.
        Truncates to `max_chars` if file is too long.
        """
        if not repo or not path:
            return ""

        clean_path = path.lstrip("/")

        # First attempt: direct raw content stream
        try:
            cmd_raw = [
                "gh", "api",
                "-H", "Accept: application/vnd.github.v3.raw",
                f"repos/{repo}/contents/{clean_path}",
            ]
            res_raw = subprocess.run(
                cmd_raw,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
            )
            if res_raw.returncode == 0 and res_raw.stdout:
                content = res_raw.stdout
                if len(content) > max_chars:
                    content = content[:max_chars] + f"\n... [Truncated to {max_chars} chars]"
                return content
        except Exception as exc:
            logger.debug("Raw content fetch failed for %s/%s: %s", repo, clean_path, exc)

        # Second attempt: standard json contents endpoint with base64 decode
        try:
            cmd_json = [
                "gh", "api",
                f"repos/{repo}/contents/{clean_path}",
            ]
            res_json = subprocess.run(
                cmd_json,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
            )
            if res_json.returncode == 0 and res_json.stdout:
                data = json.loads(res_json.stdout)
                if isinstance(data, dict) and data.get("encoding") == "base64" and "content" in data:
                    raw_bytes = base64.b64decode(data["content"].encode("ascii"))
                    content = raw_bytes.decode("utf-8", errors="replace")
                    if len(content) > max_chars:
                        content = content[:max_chars] + f"\n... [Truncated to {max_chars} chars]"
                    return content
        except Exception as exc:
            logger.warning("JSON content fetch failed for %s/%s: %s", repo, clean_path, exc)

        return ""

    def build_context_bundle(
        self,
        repo: str,
        issue_title: str,
        issue_body: str,
    ) -> Dict[str, Any]:
        """
        Builds complete context bundle containing:
        {
            "relevant_paths": [...],
            "file_snippets": {path: content, ...},
            "repo_tree_sample": [...] # top 30 relevant directory entries
        }
        Gracefully returns empty context if gh fails or repo is unavailable.
        """
        bundle: Dict[str, Any] = {
            "relevant_paths": [],
            "file_snippets": {},
            "repo_tree_sample": [],
        }

        try:
            tree = self.get_repo_tree(repo)
            if not tree:
                return bundle

            # Top relevant files
            relevant_paths = self.find_relevant_files(
                repo, issue_title, issue_body, max_files=3, tree=tree
            )
            bundle["relevant_paths"] = relevant_paths

            # Fetch snippets for top relevant files
            snippets: Dict[str, str] = {}
            for path in relevant_paths:
                content = self.fetch_file_content(repo, path)
                if content:
                    snippets[path] = content
            bundle["file_snippets"] = snippets

            # Build top 30 relevant directory entries for repo_tree_sample
            scored_all = self._score_tree_files(tree, issue_title, issue_body)
            sample_list = [p for p, _ in scored_all[:30]]
            sample_set = set(sample_list)

            if len(sample_list) < 30:
                for p in tree:
                    if p not in sample_set:
                        sample_list.append(p)
                        sample_set.add(p)
                        if len(sample_list) >= 30:
                            break

            bundle["repo_tree_sample"] = sample_list

        except Exception as exc:
            logger.warning("Error building context bundle for %s: %s", repo, exc)

        return bundle

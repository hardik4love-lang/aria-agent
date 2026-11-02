"""
ARIA Production Diff Patcher Engine.

Replaces destructive whole-file overwriting (shutil.copy2) with:
1. Precision SEARCH / REPLACE blocks (Aider-style).
2. Git unified diff verification.
3. Preserves all surrounding code, imports, licenses, and architecture.
"""

import os
import re
import logging
import subprocess
from typing import Optional, Tuple, Dict, Any, List

logger = logging.getLogger("DiffPatcher")


class DiffPatcher:
    """Applies non-destructive surgical edits to source files within a repository."""

    @staticmethod
    def apply_search_replace(file_path: str, search_block: str, replace_block: str) -> Tuple[bool, str]:
        """
        Locates the exact `search_block` in `file_path` and replaces it with `replace_block`.
        Returns (success: bool, error_or_diff: str).
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Normalize line endings
            content_norm = content.replace("\r\n", "\n")
            search_norm = search_block.replace("\r\n", "\n").strip()
            replace_norm = replace_block.replace("\r\n", "\n").strip()

            if search_norm not in content_norm:
                # Fuzzy fallback: check line-by-line whitespace stripped
                lines = content_norm.split("\n")
                search_lines = search_norm.split("\n")
                match_idx = -1

                for i in range(len(lines) - len(search_lines) + 1):
                    window = lines[i:i + len(search_lines)]
                    if [l.strip() for l in window] == [s.strip() for s in search_lines]:
                        match_idx = i
                        break

                if match_idx >= 0:
                    lines[match_idx:match_idx + len(search_lines)] = replace_norm.split("\n")
                    new_content = "\n".join(lines)
                else:
                    return False, f"Target search block not found in {os.path.basename(file_path)}"
            else:
                new_content = content_norm.replace(search_norm, replace_norm, 1)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Successfully applied search/replace patch to {file_path}")
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def parse_and_apply_aider_blocks(file_path: str, llm_diff_output: str) -> Tuple[bool, str]:
        """
        Parses standard <<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE blocks from LLM.
        """
        pattern = re.compile(
            r'<{5,9}\s*SEARCH\s*\n(.*?)\n={5,9}\s*\n(.*?)\n>{5,9}\s*REPLACE',
            re.DOTALL
        )
        matches = list(pattern.finditer(llm_diff_output))
        if not matches:
            return False, "No valid <<<<<<< SEARCH / ======= / >>>>>>> REPLACE blocks found in patch output."

        success_count = 0
        for m in matches:
            search_text = m.group(1)
            replace_text = m.group(2)
            ok, err = DiffPatcher.apply_search_replace(file_path, search_text, replace_text)
            if ok:
                success_count += 1
            else:
                logger.warning(f"Failed block: {err}")

        if success_count > 0:
            return True, f"Successfully applied {success_count} patch block(s)."
        return False, "Failed to match search blocks in target file."

    @staticmethod
    def get_git_diff(repo_path: str) -> str:
        """Returns the current git diff of the repository."""
        try:
            res = subprocess.run(
                ["git", "diff"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15
            )
            return res.stdout.strip()
        except Exception:
            return ""

    @staticmethod
    def get_diff_summary(diff_text: str) -> str:
        """Summarizes additions and deletions in the diff."""
        additions = 0
        deletions = 0
        for line in diff_text.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1
        return f"+{additions} / -{deletions} lines changed"

"""
ARIA PR Submission Audit Trail & Self-Diagnostics (Improvement #7).

PRSubmissionAuditor ensures every patch ARIA generates actually reaches GitHub:
  1. Polls GitHub API to confirm a PR is open (idempotency guard).
  2. Falls back to opening a PR directly via REST if gh CLI silently failed.
  3. Falls back further to posting the patch as a public Gist + issue comment.
  4. Logs every attempt to data/pr_audit_log.jsonl for full traceability.
"""

import os
import json
import time
import logging
import datetime
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("PRSubmissionAuditor")

_GITHUB_API = "https://api.github.com"
_GIST_API   = "https://api.github.com/gists"
_TIMEOUT    = 20.0   # seconds for every HTTP call


class PRSubmissionAuditor:
    """
    Audit-and-recovery wrapper around ARIA's PR submission pipeline.

    Usage::

        auditor = PRSubmissionAuditor(gh_token=os.environ["GH_TOKEN"])
        result  = auditor.audit_and_recover(
            repo="owner/repo",
            branch="aria/fix-issue-42-abc123",
            title="fix: resolve #42 — Foo",
            body="Closes #42 ...",
            patch_content="<unified diff or impl file text>",
            issue_number=42,
        )
        # result["status"] is one of:
        #   "PR_CONFIRMED" | "PR_OPENED_VIA_API" | "GIST_FALLBACK" | "FAILED"
    """

    AUTHOR = "hardik4love-lang"

    def __init__(self, gh_token: str, author: str = "hardik4love-lang"):
        self.gh_token = gh_token
        self.author   = author

        # Locate the data/ directory relative to this file's repo root
        # src/aria/github/pr_audit.py  →  ../../../data
        _root = Path(__file__).resolve().parent.parent.parent.parent
        self.audit_log_path = _root / "data" / "pr_audit_log.jsonl"
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Internal helpers ────────────────────────────────────────────────────

    def _headers(self) -> dict:
        """Build authorization headers for all GitHub API requests."""
        headers = {
            "Authorization": f"token {self.gh_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ARIA-Sovereign-Agent/2.0",
        }
        return headers

    def _client(self) -> httpx.Client:
        """Return a configured httpx client with default timeout."""
        return httpx.Client(timeout=_TIMEOUT, follow_redirects=True)

    # ── Public API ──────────────────────────────────────────────────────────

    def confirm_pr_opened(
        self, repo: str, branch: str, timeout_s: int = 60
    ) -> Optional[dict]:
        """
        Poll the GitHub Pulls API until a PR from `author:branch` is found
        in `repo`, or until `timeout_s` seconds elapse.

        Returns the PR data dict (with at least `html_url` and `number`) on
        success, or ``None`` if no PR is found within the timeout.
        """
        url      = f"{_GITHUB_API}/repos/{repo}/pulls"
        head_ref = f"{self.author}:{branch}"
        params   = {"head": head_ref, "state": "open", "per_page": 5}
        deadline = time.monotonic() + timeout_s

        logger.info(f"[audit] Polling for PR {head_ref} → {repo} (timeout {timeout_s}s)…")

        with self._client() as client:
            while time.monotonic() < deadline:
                try:
                    resp = client.get(url, headers=self._headers(), params=params)
                    if resp.status_code == 200:
                        prs = resp.json()
                        if prs:
                            pr = prs[0]
                            logger.info(
                                f"[audit] ✅ PR confirmed: #{pr.get('number')} — {pr.get('html_url')}"
                            )
                            return pr
                    else:
                        logger.debug(
                            f"[audit] Polls API returned HTTP {resp.status_code}"
                        )
                except Exception as exc:
                    logger.debug(f"[audit] confirm_pr_opened network error: {exc}")

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(10, remaining))

        logger.warning(f"[audit] No open PR found for {head_ref} → {repo} within {timeout_s}s.")
        return None

    def open_pr_via_api(
        self,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> Optional[dict]:
        """
        Open a pull request directly via the GitHub REST API.

        This is the primary fallback when ``gh pr create`` exits silently
        without actually creating the PR.

        Returns the created PR data dict or ``None`` on failure.
        """
        url     = f"{_GITHUB_API}/repos/{repo}/pulls"
        payload = {
            "title": title,
            "body":  body,
            "head":  f"{self.author}:{head_branch}",
            "base":  base_branch,
        }
        logger.info(f"[audit] Opening PR via REST API: {self.author}:{head_branch} → {repo}/{base_branch}")

        with self._client() as client:
            try:
                resp = client.post(url, headers=self._headers(), json=payload)
                if resp.status_code in (200, 201):
                    pr = resp.json()
                    logger.info(
                        f"[audit] ✅ PR opened via REST API: #{pr.get('number')} — {pr.get('html_url')}"
                    )
                    return pr
                else:
                    logger.warning(
                        f"[audit] REST PR create failed: HTTP {resp.status_code} — {resp.text[:300]}"
                    )
            except Exception as exc:
                logger.warning(f"[audit] open_pr_via_api exception: {exc}")

        return None

    def post_patch_as_gist(
        self, filename: str, content: str, description: str
    ) -> str:
        """
        Create a *public* GitHub Gist containing the patch.

        Returns the Gist HTML URL, or an empty string on failure.
        """
        payload = {
            "description": description,
            "public":      True,
            "files": {
                filename: {"content": content or "# Empty patch"}
            },
        }
        logger.info(f"[audit] Posting patch as Gist: {filename}")

        with self._client() as client:
            try:
                resp = client.post(_GIST_API, headers=self._headers(), json=payload)
                if resp.status_code in (200, 201):
                    gist_url = resp.json().get("html_url", "")
                    logger.info(f"[audit] ✅ Gist created: {gist_url}")
                    return gist_url
                else:
                    logger.warning(
                        f"[audit] Gist creation failed: HTTP {resp.status_code} — {resp.text[:200]}"
                    )
            except Exception as exc:
                logger.warning(f"[audit] post_patch_as_gist exception: {exc}")

        return ""

    def comment_gist_on_issue(
        self, repo: str, issue_number: int, gist_url: str, pr_title: str
    ) -> bool:
        """
        Post a comment on `issue_number` in `repo` linking to the Gist as a
        fallback submission when a PR could not be opened.

        Returns ``True`` on success.
        """
        url  = f"{_GITHUB_API}/repos/{repo}/issues/{issue_number}/comments"
        body = (
            f"🤖 **ARIA Automated Submission (Gist Fallback)**\n\n"
            f"A pull request could not be opened automatically. "
            f"The patch for **{pr_title}** has been posted as a public Gist:\n\n"
            f"📎 {gist_url}\n\n"
            f"_Payout destination: PayPal `shruhicollections@gmail.com`_"
        )
        logger.info(f"[audit] Posting Gist comment on {repo}#{issue_number}")

        with self._client() as client:
            try:
                resp = client.post(
                    url, headers=self._headers(), json={"body": body}
                )
                if resp.status_code in (200, 201):
                    logger.info(f"[audit] ✅ Gist comment posted on {repo}#{issue_number}")
                    return True
                else:
                    logger.warning(
                        f"[audit] Issue comment failed: HTTP {resp.status_code} — {resp.text[:200]}"
                    )
            except Exception as exc:
                logger.warning(f"[audit] comment_gist_on_issue exception: {exc}")

        return False

    def audit_and_recover(
        self,
        repo:          str,
        branch:        str,
        title:         str,
        body:          str,
        patch_content: str,
        issue_number:  int,
        base_branch:   str = "main",
    ) -> dict:
        """
        Full audit-and-recovery flow executed *after* every ``_submit_pr()`` call.

        Steps
        -----
        1. Check if a PR from ``{author}:{branch}`` already exists (idempotent guard).
        2. If not: attempt to open the PR directly via REST API.
        3. If REST API also fails: post the patch as a public Gist and comment
           the link on the originating issue.
        4. Append the outcome to ``data/pr_audit_log.jsonl``.

        Returns
        -------
        dict with keys:
          - ``status``: one of ``PR_CONFIRMED | PR_OPENED_VIA_API | GIST_FALLBACK | FAILED``
          - ``url``: the PR or Gist URL (empty string on ``FAILED``)
        """
        timestamp = datetime.datetime.utcnow().isoformat()
        result    = {"status": "FAILED", "url": "", "repo": repo, "branch": branch,
                     "issue_number": issue_number, "timestamp": timestamp}

        # ── Step 1: Idempotency — confirm PR already open ──────────────────
        existing_pr = self.confirm_pr_opened(repo, branch, timeout_s=60)
        if existing_pr:
            result.update({"status": "PR_CONFIRMED", "url": existing_pr.get("html_url", "")})
            self.append_audit_log({**result, "pr_number": existing_pr.get("number")})
            return result

        # ── Step 2: REST API direct PR open ───────────────────────────────
        logger.info(f"[audit] PR not found via poll — trying REST API direct open for {repo}…")
        new_pr = self.open_pr_via_api(
            repo=repo,
            title=title,
            body=body,
            head_branch=branch,
            base_branch=base_branch,
        )
        if new_pr:
            result.update({
                "status":    "PR_OPENED_VIA_API",
                "url":       new_pr.get("html_url", ""),
                "pr_number": new_pr.get("number"),
            })
            self.append_audit_log(result)
            return result

        # ── Step 3: Gist fallback ─────────────────────────────────────────
        logger.warning(
            f"[audit] REST API PR open also failed for {repo} — falling back to Gist submission."
        )
        gist_filename = f"aria_patch_{repo.replace('/', '_')}_{issue_number}.diff"
        gist_url = self.post_patch_as_gist(
            filename    = gist_filename,
            content     = patch_content or f"# Patch for {repo}#{issue_number}\n# Title: {title}\n",
            description = f"ARIA automated patch — {title} ({repo}#{issue_number})",
        )
        if gist_url:
            commented = self.comment_gist_on_issue(repo, issue_number, gist_url, title)
            result.update({
                "status":    "GIST_FALLBACK",
                "url":       gist_url,
                "commented": commented,
            })
        else:
            logger.error(f"[audit] All submission paths exhausted for {repo}#{issue_number}.")

        self.append_audit_log(result)
        return result

    def append_audit_log(self, entry: dict):
        """Append a JSON-Lines entry to ``data/pr_audit_log.jsonl``."""
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except Exception as exc:
            logger.warning(f"[audit] Could not write audit log: {exc}")

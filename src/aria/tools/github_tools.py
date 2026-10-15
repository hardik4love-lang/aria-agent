"""
GitHub Management Tools: Repository, Issue, PR, and Workflow Orchestration.
"""

import os
from typing import List, Dict, Any, Optional
from aria.security.guards import PromptInjectionGuard, CredentialRedactor


class GitHubTools:
    """Provides tools for repository management, automated PR review, and issue handling."""

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.default_repo = os.environ.get("GITHUB_REPOSITORY", "user/aria-agent")

    def gh_list_issues(self, repo: Optional[str] = None, state: str = "open") -> List[Dict[str, Any]]:
        """Lists issues in the specified repository."""
        target_repo = repo or self.default_repo
        if not self.token:
            return [
                {
                    "number": 1,
                    "title": "Evaluate memory usage in Supabase free tier",
                    "state": "open",
                    "user": "developer",
                    "comments": 2
                }
            ]

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"https://api.github.com/repos/{target_repo}/issues?state={state}",
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                return [
                    {
                        "number": item["number"],
                        "title": CredentialRedactor.redact(item["title"]),
                        "state": item["state"],
                        "user": item["user"]["login"],
                        "created_at": item["created_at"]
                    }
                    for item in data if "pull_request" not in item
                ]
        except Exception as e:
            return [{"error": f"Failed to list issues: {str(e)}"}]

    def gh_create_issue(self, title: str, body: str, repo: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new issue for task tracking or bug alerts."""
        target_repo = repo or self.default_repo
        clean_title = CredentialRedactor.redact(title)
        clean_body = CredentialRedactor.redact(body)

        if not self.token:
            return {
                "success": True,
                "status": "mock_created",
                "number": 42,
                "title": clean_title,
                "repo": target_repo
            }

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"https://api.github.com/repos/{target_repo}/issues",
                    headers=headers,
                    json={"title": clean_title, "body": clean_body}
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": True,
                    "number": data["number"],
                    "html_url": data["html_url"]
                }
        except Exception as e:
            return {"success": False, "error": f"Failed to create issue: {str(e)}"}

    def gh_read_file(self, path: str, repo: Optional[str] = None, ref: str = "main") -> Dict[str, Any]:
        """Reads file content from the target repository."""
        target_repo = repo or self.default_repo
        if not self.token:
            return {
                "path": path,
                "content": f"# Mock file content for {path} on branch {ref}\nprint('Hello ARIA')"
            }

        try:
            import httpx
            import base64
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"https://api.github.com/repos/{target_repo}/contents/{path}?ref={ref}",
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return {
                    "path": path,
                    "sha": data["sha"],
                    "content": content
                }
        except Exception as e:
            return {"error": f"Failed to read file {path}: {str(e)}"}

    def gh_review_pr(self, pr_number: int, repo: Optional[str] = None) -> Dict[str, Any]:
        """Fetches PR diff and analyzes for potential bugs, security issues, or regressions."""
        target_repo = repo or self.default_repo
        if not self.token:
            return {
                "pr_number": pr_number,
                "diff_summary": "Mock PR diff: modified 2 files (+15, -4)",
                "assessment": "No security regressions or out-of-budget dependencies detected."
            }

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3.diff"
            }
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(
                    f"https://api.github.com/repos/{target_repo}/pulls/{pr_number}",
                    headers=headers
                )
                resp.raise_for_status()
                diff_text = resp.text

            # Wrap diff with injection guard
            safe_diff = PromptInjectionGuard.wrap_external_content(diff_text[:8000], source_identifier=f"pr:{pr_number}")
            return {
                "pr_number": pr_number,
                "diff": safe_diff,
                "length_chars": len(diff_text)
            }
        except Exception as e:
            return {"error": f"Failed to fetch PR {pr_number}: {str(e)}"}

    def gh_run_workflow(self, workflow_id: str, ref: str = "main", inputs: Optional[Dict[str, Any]] = None, repo: Optional[str] = None) -> Dict[str, Any]:
        """Triggers a workflow dispatch event."""
        target_repo = repo or self.default_repo
        if not self.token:
            return {"success": True, "status": "mock_dispatched", "workflow": workflow_id}

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {"ref": ref}
            if inputs:
                payload["inputs"] = inputs

            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"https://api.github.com/repos/{target_repo}/actions/workflows/{workflow_id}/dispatches",
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()
                return {"success": True, "status": "dispatched"}
        except Exception as e:
            return {"success": False, "error": f"Failed to dispatch workflow: {str(e)}"}

"""
ARIA Production Git Workspace & Fork Manager.

Implements the complete fork-clone-branch-PR lifecycle:
1. Dynamically detects upstream default branch (main, master, develop).
2. Verifies or creates a personal fork on GitHub (hardik4love-lang/<repo>).
3. Clones or synchronizes local workspace against upstream base.
4. Creates isolated branch (aria/fix-issue-<id>).
5. Pushes to fork origin with credentials and creates clean upstream PR.
"""

import os
import sys
import json
import logging
import subprocess
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger("GitWorkspaceManager")


class GitWorkspaceManager:
    """Manages local git repositories, forks, branches, and upstream pull requests."""

    def __init__(self, workspace_root: Optional[str] = None):
        if workspace_root is None:
            # Default to D:/projects or local workspace
            workspace_root = os.getenv("ARIA_WORKSPACE_DIR", "D:/projects")
        self.workspace_root = os.path.abspath(workspace_root)
        os.makedirs(self.workspace_root, exist_ok=True)

    def _run_cmd(self, cmd: list, cwd: Optional[str] = None, timeout: int = 60) -> Tuple[int, str, str]:
        """Safely executes a shell or git command with UTF-8 encoding."""
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s: {' '.join(cmd)}"
        except Exception as e:
            return -1, "", str(e)

    def get_upstream_default_branch(self, upstream_repo: str) -> str:
        """Fetches the default branch name (main, master, etc.) from GitHub API."""
        code, out, err = self._run_cmd(["gh", "repo", "view", upstream_repo, "--json", "defaultBranchRef"])
        if code == 0 and out:
            try:
                data = json.loads(out)
                branch_ref = data.get("defaultBranchRef", {}).get("name")
                if branch_ref:
                    return branch_ref
            except Exception:
                pass
        return "main"

    def ensure_fork(self, upstream_repo: str) -> str:
        """
        Ensures a fork exists on hardik4love-lang.
        Returns the fork repository name (e.g. hardik4love-lang/omi).
        """
        repo_name = upstream_repo.split("/")[-1]
        my_fork = f"hardik4love-lang/{repo_name}"

        # Check if fork already exists
        code, out, _ = self._run_cmd(["gh", "repo", "view", my_fork, "--json", "name"])
        if code == 0:
            logger.info(f"Fork already exists: {my_fork}")
            return my_fork

        logger.info(f"Creating fork for {upstream_repo}...")
        code, out, err = self._run_cmd(["gh", "repo", "fork", upstream_repo, "--clone=false"])
        if code == 0:
            logger.info(f"Successfully created fork: {my_fork}")
            return my_fork
        else:
            logger.warning(f"Fork creation warning: {err}. Assuming fork exists or proceed with clone.")
            return my_fork

    def setup_local_workspace(self, upstream_repo: str) -> Tuple[str, str]:
        """
        Clones or syncs local repository with origin (fork) and upstream remotes.
        Returns: (local_repo_path: str, default_branch: str)
        """
        repo_name = upstream_repo.split("/")[-1]
        local_path = os.path.join(self.workspace_root, repo_name)
        default_branch = self.get_upstream_default_branch(upstream_repo)
        my_fork = f"hardik4love-lang/{repo_name}"

        if not os.path.exists(local_path):
            self.ensure_fork(upstream_repo)
            logger.info(f"Cloning fork {my_fork} into {local_path}...")
            code, out, err = self._run_cmd([
                "gh", "repo", "clone", my_fork, local_path
            ])
            if code != 0:
                # Fallback direct clone of upstream if fork failed
                logger.warning(f"Fork clone failed ({err}), cloning upstream directly...")
                self._run_cmd(["gh", "repo", "clone", upstream_repo, local_path])

        # Ensure remotes: origin = fork, upstream = target repo
        self._run_cmd(["git", "remote", "remove", "upstream"], cwd=local_path)
        self._run_cmd(["git", "remote", "add", "upstream", f"https://github.com/{upstream_repo}.git"], cwd=local_path)
        self._run_cmd(["git", "fetch", "upstream", default_branch], cwd=local_path)

        return local_path, default_branch

    def create_feature_branch(self, local_path: str, branch_name: str, base_branch: str) -> bool:
        """Creates a clean feature branch off upstream base."""
        self._run_cmd(["git", "fetch", "upstream", base_branch], cwd=local_path)
        code, _, err = self._run_cmd(["git", "checkout", "-B", branch_name, f"upstream/{base_branch}"], cwd=local_path)
        if code == 0:
            logger.info(f"Checked out branch {branch_name} tracking upstream/{base_branch}")
            return True
        logger.error(f"Failed to create branch {branch_name}: {err}")
        return False

    def push_and_create_pr(
        self,
        local_path: str,
        upstream_repo: str,
        branch_name: str,
        base_branch: str,
        title: str,
        body: str
    ) -> Optional[str]:
        """
        Pushes branch to fork origin and opens a Pull Request on upstream repository.
        Returns the PR URL if successful.
        """
        # Push to origin fork
        logger.info(f"Pushing branch {branch_name} to fork origin...")
        code, _, err = self._run_cmd(["git", "push", "-u", "origin", branch_name, "--force"], cwd=local_path)
        if code != 0:
            logger.error(f"Failed to push branch {branch_name}: {err}")
            return None

        # Check if PR already exists
        code, out, _ = self._run_cmd([
            "gh", "pr", "list",
            "--repo", upstream_repo,
            "--head", f"hardik4love-lang:{branch_name}",
            "--json", "url",
            "--state", "open"
        ], cwd=local_path)

        if code == 0 and out:
            try:
                prs = json.loads(out)
                if prs and isinstance(prs, list) and len(prs) > 0:
                    pr_url = prs[0].get("url")
                    logger.info(f"Existing open PR found: {pr_url}")
                    return pr_url
            except Exception:
                pass

        # Create upstream PR
        logger.info(f"Opening Pull Request against {upstream_repo} ({base_branch})...")
        code, out, err = self._run_cmd([
            "gh", "pr", "create",
            "--repo", upstream_repo,
            "--head", f"hardik4love-lang:{branch_name}",
            "--base", base_branch,
            "--title", title,
            "--body", body
        ], cwd=local_path)

        if code == 0 and out:
            pr_url = out.strip()
            logger.info(f"🎉 PR successfully created: {pr_url}")
            return pr_url
        else:
            logger.error(f"Failed to create PR: {err}")
            return None

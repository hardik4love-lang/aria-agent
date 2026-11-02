"""
ARIA Core SWE Agent Engine.

Unifies:
1. GitWorkspaceManager (fork, branch, upstream base resolution)
2. DiffPatcher (surgical SEARCH/REPLACE edits)
3. HermeticTestRunner (100% test pass requirement with self-healing)
4. TelegramReviewGate (operator approval card before PR creation)
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional

from aria.github.workspace_manager import GitWorkspaceManager
from aria.bounties.diff_patcher import DiffPatcher
from aria.bounties.test_runner import HermeticTestRunner
from aria.bounties.repo_context import RepoContextFetcher
from aria.security.telegram_review_gate import TelegramReviewGate
from aria.llm.router import CascadeLLMRouter

logger = logging.getLogger("AriaSWEAgent")


class AriaSWEAgent:
    """Production Autonomous Software Engineering Agent for Real Code Bounties."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace = GitWorkspaceManager(workspace_root=workspace_root)
        self.context_fetcher = RepoContextFetcher()
        self.router = CascadeLLMRouter()

    def execute_bounty_task(self, bounty: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a real bounty from issue to verified PR candidate:
        1. Setup fork & local workspace
        2. Identify target files & context
        3. Synthesize surgical diff
        4. Run native tests & verify green
        5. Push approval card to operator Telegram
        """
        repo = bounty.get("repo", "")
        number = bounty.get("number", 0)
        title = bounty.get("title", "")
        body = bounty.get("body", "")
        price = float(bounty.get("price", 100.0))
        issue_url = bounty.get("url", f"https://github.com/{repo}/issues/{number}")
        task_id = f"bounty_{repo.replace('/', '_')}_{number}"

        logger.info(f"=== Starting Real SWE Execution for {repo}#{number} (${price:.2f}) ===")

        # 1. Setup local workspace & feature branch
        local_path, base_branch = self.workspace.setup_local_workspace(repo)
        branch_name = f"aria/fix-issue-{number}"
        if not self.workspace.create_feature_branch(local_path, branch_name, base_branch):
            return {"status": "FAILED", "reason": "Could not create feature branch"}

        # 2. Ingest repo context
        context = self.context_fetcher.build_context_bundle(repo, title, body)
        relevant_paths = context.get("relevant_paths", [])
        snippets = context.get("file_snippets", {})

        if not relevant_paths:
            logger.warning("No relevant files isolated by context engine.")
            return {"status": "FAILED", "reason": "No target source files identified"}

        primary_file = relevant_paths[0]
        full_file_path = os.path.join(local_path, primary_file)

        # 3. Prompt LLM for Search/Replace block
        context_prompt = "\n\n".join(f"--- File: {p} ---\n{c}" for p, c in snippets.items())
        prompt = (
            f"You are a principal engineer fixing an issue in {repo}.\n\n"
            f"ISSUE #{number}: {title}\n"
            f"DETAILS:\n{body}\n\n"
            f"RELEVANT CODE SNIPPETS:\n{context_prompt}\n\n"
            f"TARGET FILE TO MODIFY: {primary_file}\n\n"
            f"Provide an exact, minimal SEARCH/REPLACE block fixing the bug:\n"
            f"<<<<<<< SEARCH\n"
            f"exact existing code to replace\n"
            f"=======\n"
            f"new replacement code\n"
            f">>>>>>> REPLACE"
        )

        patch_output = self.router.generate(prompt, role="executor")
        if not patch_output:
            return {"status": "FAILED", "reason": "LLM returned empty patch"}

        # 4. Apply patch non-destructively
        ok, patch_msg = DiffPatcher.parse_and_apply_aider_blocks(full_file_path, patch_output)
        if not ok:
            logger.warning(f"Could not apply block directly: {patch_msg}. Attempting self-healing...")

        # 5. Run hermetic tests & self-healing repair loop
        passed, final_diff, test_log = HermeticTestRunner.execute_self_healing_repair_loop(
            repo_path=local_path,
            target_file=primary_file,
            issue_title=title,
            issue_body=body,
            max_iterations=3
        )

        if not passed:
            logger.warning(f"Hermetic tests did not pass for {repo}#{number}. Aborting PR creation.")
            # Revert changes to keep workspace clean
            self.workspace._run_cmd(["git", "checkout", "--", "."], cwd=local_path)
            return {"status": "TESTS_FAILED", "log": test_log}

        diff_summary = DiffPatcher.get_diff_summary(final_diff)
        test_summary = "100% Native Tests Passed ✅"

        # 6. Deliver interactive approval card to Operator Telegram
        TelegramReviewGate.send_patch_for_approval(
            task_id=task_id,
            repo=repo,
            issue_number=number,
            issue_title=title,
            issue_url=issue_url,
            bounty_usd=price,
            diff_summary=diff_summary,
            diff_text=final_diff,
            test_summary=test_summary
        )

        logger.info(f"🎉 Patch verified green! Approval card pushed to Operator Telegram.")
        return {
            "status": "AWAITING_OPERATOR_APPROVAL",
            "task_id": task_id,
            "repo": repo,
            "number": number,
            "branch": branch_name,
            "diff_summary": diff_summary,
            "diff": final_diff,
            "local_path": local_path,
            "base_branch": base_branch
        }

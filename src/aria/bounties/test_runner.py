"""
ARIA Hermetic Test Runner & Self-Healing Verification Engine.

Executes native repository test suites locally:
- Python: pytest
- Go: go test -v ./...
- Rust: cargo test
- Node / TypeScript: npm test / yarn test / pnpm test / vitest

Enforces strict zero-loss rule:
If tests do not pass 100%, patches are never submitted to upstream maintainers.
"""

import os
import sys
import logging
import subprocess
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger("HermeticTestRunner")


class HermeticTestRunner:
    """Executes native test suites within cloned target repositories."""

    @staticmethod
    def detect_stack(repo_path: str) -> str:
        """Detects the primary stack of the repository."""
        if os.path.exists(os.path.join(repo_path, "go.mod")):
            return "go"
        if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
            return "rust"
        if os.path.exists(os.path.join(repo_path, "package.json")):
            return "node"
        if os.path.exists(os.path.join(repo_path, "pyproject.toml")) or os.path.exists(os.path.join(repo_path, "requirements.txt")):
            return "python"
        return "unknown"

    @classmethod
    def run_tests(
        cls,
        repo_path: str,
        test_target: Optional[str] = None,
        timeout: int = 180
    ) -> Tuple[bool, str, str]:
        """
        Runs native repository tests.
        Returns: (passed: bool, full_output: str, error_summary: str)
        """
        stack = cls.detect_stack(repo_path)
        logger.info(f"Running hermetic tests in {repo_path} (detected stack: {stack})...")

        if stack == "python":
            cmd = ["python", "-m", "pytest"]
            if test_target:
                cmd.append(test_target)
            else:
                cmd.extend(["-v", "--maxfail=3"])
        elif stack == "go":
            cmd = ["go", "test", "-v"]
            if test_target:
                cmd.append(test_target)
            else:
                cmd.append("./...")
        elif stack == "rust":
            cmd = ["cargo", "test"]
            if test_target:
                cmd.extend(["--test", test_target])
        elif stack == "node":
            if os.path.exists(os.path.join(repo_path, "pnpm-lock.yaml")):
                cmd = ["pnpm", "test"]
            elif os.path.exists(os.path.join(repo_path, "yarn.lock")):
                cmd = ["yarn", "test"]
            else:
                cmd = ["npm", "test"]
            if test_target:
                cmd.extend(["--", test_target])
        else:
            return False, "Unknown stack: cannot find native test runner.", "NO_TEST_RUNNER"

        try:
            res = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            output = (res.stdout + "\n" + res.stderr).strip()
            passed = (res.returncode == 0)

            if passed:
                logger.info(f"✅ Hermetic tests passed in {repo_path} (stack: {stack})")
                return True, output, ""
            else:
                logger.warning(f"❌ Hermetic tests failed with returncode {res.returncode}")
                # Extract last 20 lines of failure output
                lines = output.splitlines()
                summary = "\n".join(lines[-25:])
                return False, output, summary

        except subprocess.TimeoutExpired:
            return False, f"Test execution timed out after {timeout}s", "TIMEOUT"
        except Exception as e:
            return False, str(e), type(e).__name__

    @classmethod
    def execute_self_healing_repair_loop(
        cls,
        repo_path: str,
        target_file: str,
        issue_title: str,
        issue_body: str,
        test_target: Optional[str] = None,
        max_iterations: int = 3
    ) -> Tuple[bool, str, str]:
        """
        Iteratively runs tests, captures errors, and re-prompts the LLM to patch until green.
        Returns: (passed: bool, final_diff: str, log: str)
        """
        from aria.bounties.diff_patcher import DiffPatcher
        from aria.llm.router import CascadeLLMRouter

        router = CascadeLLMRouter()

        for iteration in range(1, max_iterations + 1):
            logger.info(f"Self-healing iteration {iteration}/{max_iterations}...")
            passed, out, summary = cls.run_tests(repo_path, test_target=test_target)
            if passed:
                diff = DiffPatcher.get_git_diff(repo_path)
                return True, diff, f"Tests passed on iteration {iteration}."

            logger.info(f"Tests failed on iteration {iteration}. Generating repair patch...")
            repair_prompt = (
                f"You are repairing a patch that failed tests on {os.path.basename(repo_path)}.\n\n"
                f"ISSUE TITLE: {issue_title}\n"
                f"ISSUE DESCRIPTION: {issue_body}\n\n"
                f"TEST FAILURE OUTPUT:\n{summary}\n\n"
                f"Return an exact Aider-style SEARCH / REPLACE block to fix the failure:\n"
                f"<<<<<<< SEARCH\n"
                f"code to replace\n"
                f"=======\n"
                f"replacement code\n"
                f">>>>>>> REPLACE"
            )

            try:
                patch_response = router.generate(repair_prompt, role="executor")
                if patch_response:
                    full_target_path = os.path.join(repo_path, target_file)
                    DiffPatcher.parse_and_apply_aider_blocks(full_target_path, patch_response)
            except Exception as e:
                logger.error(f"Error during repair generation: {e}")

        # Final test pass
        passed, out, summary = cls.run_tests(repo_path, test_target=test_target)
        diff = DiffPatcher.get_git_diff(repo_path)
        return passed, diff, out if passed else summary

"""
Tests for RepoContextFetcher and RealBountySolver deep repository context integration.
"""

import os
import json
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from aria.bounties.repo_context import RepoContextFetcher
from aria.bounties.real_bounty_solver import RealBountySolver


def test_repo_context_fetcher_filtering():
    fetcher = RepoContextFetcher()
    mock_tree_json = {
        "tree": [
            {"path": "src/core/auth.py", "type": "blob"},
            {"path": "src/core/user.ts", "type": "blob"},
            {"path": "node_modules/pkg/index.js", "type": "blob"},
            {"path": ".git/config", "type": "blob"},
            {"path": "package-lock.json", "type": "blob"},
            {"path": "assets/banner.png", "type": "blob"},
            {"path": "build/app.min.js", "type": "blob"},
            {"path": "src/core", "type": "tree"},
        ]
    }

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_tree_json),
            stderr="",
        )
        tree = fetcher.get_repo_tree("test-org/test-repo")

        assert "src/core/auth.py" in tree
        assert "src/core/user.ts" in tree
        assert "node_modules/pkg/index.js" not in tree
        assert ".git/config" not in tree
        assert "package-lock.json" not in tree
        assert "assets/banner.png" not in tree
        assert "build/app.min.js" not in tree
        assert "src/core" not in tree


def test_repo_context_branch_fallback():
    fetcher = RepoContextFetcher()

    def mock_subproc(cmd, **kwargs):
        # Fail on main, succeed on master
        if "main" in cmd[2]:
            return MagicMock(returncode=1, stdout="", stderr="Branch not found")
        return MagicMock(
            returncode=0,
            stdout=json.dumps({"tree": [{"path": "main.py", "type": "blob"}]}),
            stderr="",
        )

    with patch("subprocess.run", side_effect=mock_subproc):
        tree = fetcher.get_repo_tree("test-org/fallback-repo")
        assert tree == ["main.py"]


def test_find_relevant_files_explicit_and_keywords():
    fetcher = RepoContextFetcher()
    sample_tree = [
        "packages/server/src/auth/token_verifier.ts",
        "packages/server/src/auth/token_verifier.spec.ts",
        "packages/server/src/user/profile.ts",
        "packages/common/utils/date.ts",
        "packages/client/components/button.tsx",
    ]

    # Explicit path match in body
    matched = fetcher.find_relevant_files(
        repo="org/repo",
        issue_title="Token verification drops claim",
        issue_body="Look at `packages/server/src/auth/token_verifier.ts` for the handler",
        max_files=2,
        tree=sample_tree,
    )
    assert len(matched) >= 1
    assert matched[0] == "packages/server/src/auth/token_verifier.ts"

    # Keyword match from title
    matched_kw = fetcher.find_relevant_files(
        repo="org/repo",
        issue_title="User profile update fails",
        issue_body="Database update does not persist user name",
        max_files=1,
        tree=sample_tree,
    )
    assert matched_kw == ["packages/server/src/user/profile.ts"]


def test_fetch_file_content_and_truncation():
    fetcher = RepoContextFetcher()

    long_content = "const x = 1;\n" * 500  # ~6500 chars

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=long_content, stderr="")
        snippet = fetcher.fetch_file_content("org/repo", "src/long.ts", max_chars=200)

        assert len(snippet) <= 250
        assert "Truncated to 200 chars" in snippet


def test_build_context_bundle():
    fetcher = RepoContextFetcher()
    sample_tree = [f"src/module_{i}.ts" for i in range(40)]

    with patch.object(fetcher, "get_repo_tree", return_value=sample_tree):
        with patch.object(fetcher, "fetch_file_content", return_value="export const a = 1;"):
            bundle = fetcher.build_context_bundle(
                repo="org/repo",
                issue_title="Fix module 5 export",
                issue_body="Check src/module_5.ts",
            )

            assert "relevant_paths" in bundle
            assert "file_snippets" in bundle
            assert "repo_tree_sample" in bundle
            assert len(bundle["repo_tree_sample"]) == 30
            assert "src/module_5.ts" in bundle["relevant_paths"]
            assert "src/module_5.ts" in bundle["file_snippets"]


def test_real_bounty_solver_with_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_fetcher = MagicMock()
        mock_fetcher.build_context_bundle.return_value = {
            "relevant_paths": ["src/auth/service.py"],
            "file_snippets": {"src/auth/service.py": "def verify(): pass"},
            "repo_tree_sample": ["src/auth/service.py", "src/main.py"],
        }

        solver = RealBountySolver(output_dir=tmpdir, context_fetcher=mock_fetcher)
        assert solver.context_fetcher is mock_fetcher

        issue = {
            "id": "task_999",
            "title": "Fix token expiration in auth service",
            "repo": "example/auth-service",
            "price": "100 USD",
            "body": "Token expires too early in service.py",
        }

        with patch("aria.llm.router.CascadeLLMRouter.generate", return_value="def verify(): return True") as mock_gen:
            res = solver.solve_bounty(issue)

            assert res["status"] == "SOLVED_AND_VERIFIED"
            assert "target_files" in res
            assert res["target_files"] == ["src/auth/service.py"]
            assert res["relevant_paths"] == ["src/auth/service.py"]

            # Verify prompt received the snippets and instructions
            impl_call_args = mock_gen.call_args_list[0][0][0]
            assert "EXISTING REPOSITORY CONTEXT:" in impl_call_args
            assert "src/auth/service.py" in impl_call_args
            assert "def verify(): pass" in impl_call_args
            assert "Fix or modify the relevant existing file(s) directly. Do not create unnecessary new files if modifying an existing file is appropriate." in impl_call_args

            mock_fetcher.build_context_bundle.assert_called_once_with(
                "example/auth-service",
                "Fix token expiration in auth service",
                "Token expires too early in service.py",
            )

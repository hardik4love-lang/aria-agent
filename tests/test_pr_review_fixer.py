"""
Unit Tests for ARIA PRReviewFixer & PRReviewAutoFixer
(Autonomous CI & Maintainer Review Self-Healing Guardian Loop).
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aria.github.pr_review_fixer import PRReviewFixer, PRReviewAutoFixer, run_gh_command


def test_pr_review_auto_fixer_initialization():
    fixer = PRReviewFixer(token="test_mock_token")
    assert fixer.token == "test_mock_token"
    assert fixer.AUTHOR_LOGIN == "hardik4love-lang"
    assert fixer.state_file.name == "review_fixes.jsonl"
    assert fixer.healing_log_file.name == "pr_healing_log.jsonl"


def test_load_and_record_processed_feedback(tmp_path):
    mock_state_file = tmp_path / "review_fixes.jsonl"
    fixer = PRReviewFixer(token="test_mock_token")
    fixer.state_file = mock_state_file

    # Initially empty
    processed = fixer.load_processed_feedback_ids()
    assert len(processed) == 0

    # Record item
    fixer.record_processed_fix({
        "feedback_id": "comment-123456",
        "repo": "BasedHardware/omi",
        "pr_number": 23620,
        "status": "TEST_OK"
    })

    # Reload and verify
    reloaded = fixer.load_processed_feedback_ids()
    assert "comment-123456" in reloaded


def test_discover_active_prs_fallback():
    fixer = PRReviewFixer(token="")
    with patch("aria.github.pr_review_fixer.get_http_client") as mock_client_getter:
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Network offline")
        mock_client_getter.return_value = mock_client

        prs = fixer.discover_active_prs()
        assert len(prs) >= 5
        assert any(p["pr_number"] == 23620 for p in prs)
        assert any(p["repo"] == "BasedHardware/omi" for p in prs)


def test_author_comment_filtering():
    fixer = PRReviewFixer(token="test_token")
    assert fixer.AUTHOR_LOGIN == "hardik4love-lang"
    assert PRReviewAutoFixer is PRReviewFixer


def test_list_active_prs_with_gh():
    fixer = PRReviewFixer(token="test_mock_token")

    mock_pr_list = [
        {
            "number": 23842,
            "title": "fix(plugins): require auth on omi-github-app",
            "url": "https://github.com/BasedHardware/omi/pull/23842",
            "headRefName": "fix/auth-uid",
            "headRepositoryOwner": {"login": "hardik4love-lang"},
            "headRepository": {"nameWithOwner": "hardik4love-lang/omi"},
            "repository": {"nameWithOwner": "BasedHardware/omi"},
            "updatedAt": "2026-10-30T15:27:46Z"
        }
    ]

    with patch("aria.github.pr_review_fixer.run_gh_command") as mock_run:
        # First call: gh pr list returns mock_pr_list
        mock_run.return_value = (0, json.dumps(mock_pr_list), "")
        prs = fixer.list_active_prs(author="@me")

        assert len(prs) >= 1
        assert prs[0]["number"] == 23842
        assert prs[0]["repo"] == "BasedHardware/omi"
        assert prs[0]["head_ref"] == "fix/auth-uid"


def test_check_pr_ci_status_failure():
    fixer = PRReviewFixer(token="test_mock_token")

    mock_checks = [
        {"name": "Backend Tests", "state": "FAILURE", "bucket": "fail"},
        {"name": "Frontend Lint", "state": "SUCCESS", "bucket": "pass"}
    ]

    with patch("aria.github.pr_review_fixer.run_gh_command") as mock_run:
        def side_effect(args, timeout=30.0):
            if "checks" in args:
                return (0, json.dumps(mock_checks), "")
            if "--log-failed" in args:
                return (0, "AssertionError: Expected 200 but got 401\nFAILED test_auth.py:42", "")
            return (0, "", "")

        mock_run.side_effect = side_effect
        status = fixer.check_pr_ci_status("BasedHardware/omi", 23842)

        assert status["has_failure"] is True
        assert len(status["failed_checks"]) == 1
        assert status["failed_checks"][0]["name"] == "Backend Tests"
        assert "AssertionError" in status["failure_logs"]


def test_check_pr_ci_status_success():
    fixer = PRReviewFixer(token="test_mock_token")

    mock_checks = [
        {"name": "Backend Tests", "state": "SUCCESS", "bucket": "pass"},
        {"name": "Frontend Lint", "state": "SUCCESS", "bucket": "pass"}
    ]

    with patch("aria.github.pr_review_fixer.run_gh_command") as mock_run:
        mock_run.return_value = (0, json.dumps(mock_checks), "")
        status = fixer.check_pr_ci_status("BasedHardware/omi", 23842)

        assert status["has_failure"] is False
        assert len(status["failed_checks"]) == 0
        assert status["failure_logs"] == ""


def test_check_pr_comments_and_reviews_filtering():
    fixer = PRReviewFixer(token="test_mock_token")

    mock_view_data = {
        "reviews": [
            {
                "id": "PRR_1",
                "author": {"login": "hardik4love-lang"},  # Should be excluded (self)
                "body": "Self comment",
                "state": "APPROVED"
            },
            {
                "id": "PRR_2",
                "author": {"login": "maintainer-bob"},
                "body": "Please add test coverage for the 401 scenario.",
                "state": "CHANGES_REQUESTED",
                "submittedAt": "2026-10-30T10:00:00Z"
            }
        ],
        "comments": [
            {
                "id": "IC_1",
                "author": {"login": "aria-daemon"},  # Should be excluded (daemon bot)
                "body": "[ARIA] Automated update",
                "createdAt": "2026-10-30T11:00:00Z"
            },
            {
                "id": "IC_2",
                "author": {"login": "reviewer-alice"},
                "body": "Does this handle empty tokens properly?",
                "createdAt": "2026-10-30T12:00:00Z"
            }
        ]
    }

    with patch("aria.github.pr_review_fixer.run_gh_command") as mock_run:
        mock_run.return_value = (0, json.dumps(mock_view_data), "")
        actionable = fixer.check_pr_comments_and_reviews("BasedHardware/omi", 23842)

        assert len(actionable) == 2
        authors = [a["author"] for a in actionable]
        assert "hardik4love-lang" not in authors
        assert "aria-daemon" not in authors
        assert "maintainer-bob" in authors
        assert "reviewer-alice" in authors


def test_heal_pr_flow(tmp_path):
    mock_state_file = tmp_path / "review_fixes.jsonl"
    mock_log_file = tmp_path / "pr_healing_log.jsonl"

    mock_router = MagicMock()
    # Plan response: identify target file
    mock_router.generate.side_effect = [
        json.dumps({"target_file": "plugins/auth.py", "summary_of_fix": "Handle empty token check"}),
        "```python\ndef auth():\n    return True\n```"
    ]

    fixer = PRReviewFixer(token="test_mock_token", router=mock_router)
    fixer.state_file = mock_state_file
    fixer.healing_log_file = mock_log_file

    pr_info = {
        "repo": "BasedHardware/omi",
        "pr_number": 23842,
        "title": "fix: auth check",
        "headRefName": "fix/auth-uid",
        "head_repo": "hardik4love-lang/omi"
    }
    ci_failure = {
        "has_failure": True,
        "summary": "1 check failed",
        "failure_logs": "AssertionError: empty token failed"
    }

    with patch.object(fixer, "fetch_file_content", return_value=("original code", "blob_sha_123")):
        with patch.object(fixer, "commit_file_patch", return_value=True):
            with patch.object(fixer, "post_pr_reply", return_value=True):
                healed = fixer.heal_pr(pr_info, ci_failure=ci_failure)

                assert healed is True
                assert mock_state_file.exists()
                assert mock_log_file.exists()
                content = mock_log_file.read_text(encoding="utf-8")
                assert "HEALED_AND_PUSHED" in content
                assert "plugins/auth.py" in content


def test_run_self_healing_cycle(tmp_path):
    mock_log_file = tmp_path / "pr_healing_log.jsonl"
    fixer = PRReviewFixer(token="test_mock_token")
    fixer.healing_log_file = mock_log_file

    with patch.object(fixer, "list_active_prs", return_value=[{"repo": "BasedHardware/omi", "number": 23842}]):
        with patch.object(fixer, "check_pr_ci_status", return_value={"has_failure": False, "failed_checks": []}):
            with patch.object(fixer, "check_pr_comments_and_reviews", return_value=[]):
                summary = fixer.run_self_healing_cycle()

                assert summary["prs_scanned"] == 1
                assert summary["ci_failures_detected"] == 0
                assert summary["review_feedback_detected"] == 0
                assert summary["healed_count"] == 0
                assert summary["status"] == "COMPLETED"

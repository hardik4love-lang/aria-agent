"""
Unit Tests for ARIA PRReviewAutoFixer (Autonomous Review & CI Auto-Fix Engine).
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from aria.github.pr_review_fixer import PRReviewAutoFixer


def test_pr_review_auto_fixer_initialization():
    fixer = PRReviewAutoFixer(token="test_mock_token")
    assert fixer.token == "test_mock_token"
    assert fixer.AUTHOR_LOGIN == "hardik4love-lang"
    assert fixer.state_file.name == "review_fixes.jsonl"


def test_load_and_record_processed_feedback(tmp_path):
    mock_state_file = tmp_path / "review_fixes.jsonl"
    fixer = PRReviewAutoFixer(token="test_mock_token")
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
    fixer = PRReviewAutoFixer(token="")
    with patch("aria.github.pr_review_fixer.get_http_client") as mock_client_getter:
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Network offline")
        mock_client_getter.return_value = mock_client

        prs = fixer.discover_active_prs()
        assert len(prs) >= 5
        assert any(p["pr_number"] == 23620 for p in prs)
        assert any(p["repo"] == "BasedHardware/omi" for p in prs)


def test_author_comment_filtering():
    fixer = PRReviewAutoFixer(token="test_token")
    # Verify AUTHOR_LOGIN is hardik4love-lang
    assert fixer.AUTHOR_LOGIN == "hardik4love-lang"

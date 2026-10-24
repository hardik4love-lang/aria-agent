"""
Tests for ARIA Priority 1 Upgrades:
- Dynamic Pricing Engine
- Daily Executive Intelligence Briefing
- In-Memory Quota Write-Behind Cache
- PR Rebase Watcher
- Standardized 3-File Deliverables
"""

import os
import json
import tempfile
import pytest
from datetime import datetime, timezone

from aria.bounties.pricing_engine import DynamicPricingEngine
from aria.briefing.daily_briefing import DailyBriefingEngine
from aria.llm.quota import QuotaTracker
from aria.github.rebase_watcher import PRRebaseWatcher


def test_pricing_engine_multipliers():
    """Verifies that urgency and complexity keywords scale multipliers accurately."""
    # Standard task
    m_u1, m_c1, m_r1 = DynamicPricingEngine.calculate_multipliers("Fix button padding in CSS")
    assert m_u1 == 1.0
    assert m_c1 <= 1.0

    # Urgent and high-complexity task
    m_u2, m_c2, m_r2 = DynamicPricingEngine.calculate_multipliers(
        "Urgent: Production down due to memory leak and race condition in reverse proxy"
    )
    assert m_u2 > 1.0
    assert m_c2 > 1.0


def test_pricing_engine_tiered_proposals():
    """Verifies standard vs turnkey +40% pricing proposal generation."""
    proposal = DynamicPricingEngine.generate_tiered_proposal(
        "Critical auth deadlock in Go service",
        base_rate=50.0
    )
    assert "proposal_text" in proposal
    assert "Standard Fix" in proposal["proposal_text"]
    assert "Turnkey Enterprise Package" in proposal["proposal_text"]
    assert "shruhicollections@gmail.com" in proposal["proposal_text"]
    assert proposal["pricing_data"]["turnkey_premium_pct"] == 40


def test_daily_briefing_card_generation():
    """Verifies that daily briefing card contains complete financial and infrastructure ledger."""
    card = DailyBriefingEngine.generate_briefing_card()
    assert "ARIA EXECUTIVE BRIEFING" in card
    assert "$6,455.00 USD" in card
    assert "Tenstorrent #60777" in card
    assert "HackerOne #4115591" in card
    assert "Go-Hybrid #825" in card
    assert "shruhicollections@gmail.com" in card
    assert "0xFa53f547" in card
    assert "hardik4love-lang.github.io/aria-agent" in card


def test_daily_briefing_dispatch_state_tracking():
    """Verifies dispatch deduplication via state file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "last_briefing.json")
        now_hour = datetime.now(timezone.utc).hour

        # Before dispatching
        should_disp = DailyBriefingEngine.should_dispatch_today(check_hour=now_hour, state_file=state_file)
        assert should_disp is True

        # Record dispatch
        DailyBriefingEngine.record_dispatch(state_file=state_file)

        # After dispatching today, should not dispatch again
        should_disp_after = DailyBriefingEngine.should_dispatch_today(check_hour=now_hour, state_file=state_file)
        assert should_disp_after is False


def test_in_memory_quota_cache_flush():
    """Verifies in-memory write-behind cache and persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "quota.json")
        tracker = QuotaTracker(state_file_path=state_file)

        tracker.record_call("groq", count=25)
        snap = tracker.get_snapshot()
        assert snap["groq_requests_today"] == 25
        assert snap["groq_remaining"] == 14400 - 25

        # Verify flushed to disk
        assert os.path.exists(state_file)
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data.get("groq_calls") == 25


def test_pr_rebase_watcher_health_check():
    """Verifies PRRebaseWatcher inspects tracked repositories."""
    watcher = PRRebaseWatcher()
    results = watcher.inspect_all_tracked_prs()
    assert len(results) == 2
    ids = [r["id"] for r in results]
    assert "tt-60777" in ids
    assert "hy-825" in ids
    for r in results:
        assert "health" in r
        assert "status" in r["health"]


def test_standardized_deliverable_bundle():
    """Verifies that generate_standard_package outputs code, test suite, and README."""
    from aria.bounties.autonomous_solvers import AutonomousJobSolvers
    pkg = AutonomousJobSolvers.generate_standard_package("job-01")
    assert pkg["status"] == "BUNDLE_GENERATED"
    files = pkg["files"]
    assert os.path.exists(files["implementation"])
    assert os.path.exists(files["test_suite"])
    assert os.path.exists(files["readme"])
    with open(files["readme"], "r", encoding="utf-8") as f:
        readme_text = f.read()
        assert "Root Cause & Architecture" in readme_text
        assert "shruhicollections@gmail.com" in readme_text


def test_http_connection_pool():
    """Verifies centralized HTTP client pooling and reuse."""
    from aria.utils.http import get_http_client, close_http_clients
    c1 = get_http_client()
    c2 = get_http_client()
    assert c1 is c2
    assert not c1.is_closed
    close_http_clients()


def test_submission_lifecycle_evaluation():
    """Verifies that submissions are accurately evaluated for T+6h, T+18h, and T+48h stages."""
    from aria.bounties.submission_engine import BountySubmissionEngine
    lifecycle = BountySubmissionEngine.evaluate_submission_lifecycle()
    assert isinstance(lifecycle, list)
    if lifecycle:
        first = lifecycle[0]
        assert "submission_id" in first
        assert "lifecycle_stage" in first
        assert "action_required" in first

        msg = BountySubmissionEngine.generate_followup_message(first["submission_id"])
        assert "followup_text" in msg
        assert "shruhicollections@gmail.com" in msg["followup_text"]

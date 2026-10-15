"""
Tests for quota tracking and zero-cost guardrails.
"""

import os
import tempfile
from aria.llm.quota import QuotaTracker


def test_quota_tracking_and_depletion():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "quota.json")
        tracker = QuotaTracker(state_file_path=state_file)

        initial = tracker.get_snapshot()
        assert initial["groq_requests_today"] == 0
        assert initial["groq_remaining"] == 14400

        # Record 100 Groq calls
        tracker.record_call("groq", count=100)
        updated = tracker.get_snapshot()
        assert updated["groq_requests_today"] == 100
        assert updated["groq_remaining"] == 14300

        # Record large batch to trigger failover logic
        tracker.record_call("groq", count=12500)
        depleted = tracker.get_snapshot()
        # With less than 2000 remaining, recommended provider should switch
        assert depleted["active_provider"] != "groq"

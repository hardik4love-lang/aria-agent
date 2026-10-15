"""
Tests for state structures and Pydantic schemas.
"""

from aria.state import PlanStep, ToolObservation, QuotaSnapshot


def test_plan_step_schema():
    step = PlanStep(
        step_id=1,
        description="List unread emails",
        tool_name="email_list_unread",
        tool_arguments={"max_count": 5},
        is_high_risk=False
    )
    assert step.step_id == 1
    assert step.status == "pending"
    assert step.tool_arguments["max_count"] == 5


def test_tool_observation_schema():
    obs = ToolObservation(
        tool_name="email_read",
        inputs={"uid": "123"},
        output="Email body content",
        success=True,
        timestamp="2026-10-15T12:00:00Z",
        duration_ms=45
    )
    assert obs.tool_name == "email_read"
    assert obs.success is True
    assert obs.duration_ms == 45


def test_quota_snapshot_defaults():
    q = QuotaSnapshot()
    assert q.groq_remaining == 14400
    assert q.gemini_remaining == 1500
    assert q.github_remaining == 5000
    assert q.active_provider == "groq"

"""
Chaos Engineering and Resilience Test Suite.
Validates zero-cost compliance, graceful degradation, and error recovery under adverse conditions.
"""

import time
import tempfile
from aria.llm.quota import QuotaTracker
from aria.llm.router import ModelRouter, GroqClient, GeminiClient, MockLLMClient
from aria.storage.checkpointer import CheckpointManager
from aria.nodes import NodeRegistry
from aria.state import AgentState


def test_chaos_groq_quota_exhaustion_failover():
    """Simulates Groq daily rate limit exhaustion and verifies automatic failover."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = QuotaTracker(state_file_path=f"{tmpdir}/quota.json")
        # Artificially consume Groq quota down to buffer threshold
        tracker.record_call("groq", count=13000)

        snapshot = tracker.get_snapshot()
        assert snapshot["groq_remaining"] <= tracker.BUFFERS["groq_reserve"]

        router = ModelRouter(quota_tracker=tracker)
        router.gemini_key = "test_gemini_key"
        router.groq_key = "test_groq_key"

        client = router.get_client(role="planner")
        # Should NOT be Groq because quota is exhausted
        assert not isinstance(client, GroqClient)
        assert isinstance(client, GeminiClient)


def test_chaos_all_cloud_quotas_exhausted():
    """Simulates both Groq and Gemini exhaustion and verifies fallback to local/mock."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = QuotaTracker(state_file_path=f"{tmpdir}/quota.json")
        tracker.record_call("groq", count=14000)
        tracker.record_call("gemini", count=1450)

        router = ModelRouter(quota_tracker=tracker)
        router.gemini_key = "test_gemini_key"
        router.groq_key = "test_groq_key"
        router.ollama_url = "http://127.0.0.1:59999"  # Offline mock

        client = router.get_client(role="executor")
        assert isinstance(client, MockLLMClient)


def test_chaos_corrupted_checkpoint_recovery():
    """Simulates corrupted checkpoint JSON and verifies manager handles it safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CheckpointManager(local_dir=tmpdir)
        # Write corrupted JSON
        latest_file = f"{tmpdir}/task_bad_latest.json"
        with open(latest_file, "w") as f:
            f.write("{ INVALID JSON DATA !@#$ }")

        resumed = manager.load_checkpoint("task_bad")
        assert resumed is None  # Handled cleanly without unhandled exception


def test_chaos_faulty_tool_execution():
    """Simulates tool crash and verifies state captures error without aborting graph."""
    registry = NodeRegistry()
    state: AgentState = {
        "task_id": "test_chaos_task",
        "task_type": "adhoc",
        "task_description": "Execute non-existent tool",
        "raw_input": {"job_start_epoch": time.time(), "max_job_seconds": 1000},
        "plan": [
            {
                "step_id": 1,
                "description": "Call broken tool",
                "tool_name": "non_existent_tool_xyz",
                "tool_arguments": {},
                "is_high_risk": False,
                "status": "pending"
            }
        ],
        "current_step_idx": 0,
        "observations": [],
        "messages": [],
        "quota_snapshot": registry.router.quota.get_snapshot(),
        "checkpoint_version": 1,
        "error_count": 0,
        "human_approval_required": False,
        "pending_action": None,
        "approval_status": None,
        "checkpoint_and_pause": False,
        "completion_status": "in_progress",
        "audit_log": []
    }

    updated_state = registry.executor_node(state)
    assert updated_state["error_count"] == 1
    assert len(updated_state["observations"]) == 1
    assert updated_state["observations"][0]["success"] is False
    assert "Unknown tool" in updated_state["observations"][0]["error"]

"""
End-to-end workflow execution tests for the LangGraph agent graph.
"""

import time
import tempfile
from aria.graph import build_aria_graph
from aria.nodes import NodeRegistry
from aria.state import AgentState


def test_full_agent_workflow():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = NodeRegistry()
        # Point memory and checkpoints to temp directory
        registry.checkpointer.local_dir = f"{tmpdir}/checkpoints"
        registry.git_store.root_dir = tmpdir
        registry.git_store.state_dir = f"{tmpdir}/state"
        registry.git_store.logs_dir = f"{tmpdir}/state/logs"

        app = build_aria_graph(registry=registry)

        state: AgentState = {
            "task_id": "test_task_001",
            "task_type": "adhoc",
            "task_description": "Review unread emails and record summary in memory",
            "raw_input": {
                "job_start_epoch": time.time(),
                "max_job_seconds": 3600,
                "dry_run": True
            },
            "plan": [],
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

        final_state = app.invoke(state)

        assert final_state["task_id"] == "test_task_001"
        assert final_state["completion_status"] == "completed"
        assert len(final_state["plan"]) >= 1
        assert len(final_state["observations"]) >= 1
        assert final_state["current_step_idx"] >= 1

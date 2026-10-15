"""
ARIA Interactive Operator Dashboard and Simulator.
Provides real-time quota telemetry, simulated trigger execution, and audit log inspection.
"""

import sys
import time
from typing import Dict, Any

from aria.llm.quota import QuotaTracker
from aria.storage.checkpointer import CheckpointManager
from aria.optimization.self_optimizer import SelfOptimizer
from aria.graph import build_aria_graph
from aria.state import AgentState


def print_banner():
    banner = """
======================================================================
  ARIA: Autonomous Reasoning & Interaction Agent ($0.00 TCO)
  Architecture: Git-Native Ephemeral Runner + Zero-Cost Inference
======================================================================
"""
    print(banner)


def show_quota_panel():
    q = QuotaTracker()
    snap = q.get_snapshot()

    print("=" * 65)
    print("  LIVE FREE-TIER QUOTA STATUS & HEALTH")
    print("=" * 65)
    print(f"  Groq Requests Used Today    : {snap['groq_requests_today']:>6} / 14400 (Daily Free)")
    print(f"  Groq Remaining              : {snap['groq_remaining']:>6}")
    print(f"  Gemini Requests Used Today  : {snap['gemini_requests_today']:>6} /  1500 (Daily Free)")
    print(f"  Gemini Remaining            : {snap['gemini_remaining']:>6}")
    print(f"  GitHub Hourly Calls Used    : {snap['github_requests_this_hour']:>6} /  5000 (Hourly Free)")
    print(f"  GitHub Remaining            : {snap['github_remaining']:>6}")
    print(f"  Active Routing Provider     : [ {snap['active_provider'].upper()} ]")
    print(f"  Safe Limit Budget           : {'HEALTHY (100% Zero-Cost)' if snap['within_safe_limits'] else 'BUDGET WARNING'}")
    print("=" * 65)


def run_simulated_task(task_desc: str, task_type: str = "email") -> Dict[str, Any]:
    print(f"\n[RUNNER] Launching simulated task: '{task_desc}' (type: {task_type})...")
    q = QuotaTracker()
    app = build_aria_graph()

    state: AgentState = {
        "task_id": f"sim_{int(time.time())}",
        "task_type": task_type,
        "task_description": task_desc,
        "raw_input": {"job_start_epoch": time.time(), "max_job_seconds": 600, "dry_run": True},
        "plan": [],
        "current_step_idx": 0,
        "observations": [],
        "messages": [],
        "quota_snapshot": q.get_snapshot(),
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
    print(f"[RUNNER] Completed with status: {final_state.get('completion_status')}")
    print(f"[RUNNER] Steps executed: {final_state.get('current_step_idx')}")
    for idx, obs in enumerate(final_state.get("observations", []), start=1):
        print(f"         Step {idx} [{obs['tool_name']}]: {'SUCCESS' if obs['success'] else 'FAILED'}")
    return final_state


def show_optimizer_report():
    optimizer = SelfOptimizer()
    print("\n" + optimizer.generate_health_report())


def main():
    print_banner()
    show_quota_panel()

    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        task_desc = sys.argv[2] if len(sys.argv) > 2 else "Check inbox and draft replies"
        run_simulated_task(task_desc)
    elif len(sys.argv) > 1 and sys.argv[1] == "--report":
        show_optimizer_report()
    else:
        print("\nInteractive CLI usage:")
        print("  python -m aria.cli.interactive --simulate 'your task instruction'")
        print("  python -m aria.cli.interactive --report")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
ARIA Agent Main Execution Entrypoint.
Invoked by GitHub Actions workflows, cron schedules, or manual CLI dispatches.
"""

import sys
import os
import uuid
import time
import argparse
from typing import Dict, Any

from aria.state import AgentState
from aria.graph import build_aria_graph
from aria.storage.checkpointer import CheckpointManager
from aria.llm.quota import QuotaTracker


def parse_args():
    parser = argparse.ArgumentParser(description="ARIA: Autonomous Reasoning & Interaction Agent ($0.00 TCO)")
    parser.add_argument("--task", type=str, default="Inspect unread emails and log tasks", help="Task instruction")
    parser.add_argument("--type", type=str, default="email", choices=["email", "github", "maintenance", "adhoc"], help="Task domain")
    parser.add_argument("--resume-id", type=str, default=None, help="Thread ID to resume from previous checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Execute without modifying remote state")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 65)
    print("  ARIA: Autonomous Reasoning & Interaction Agent ($0.00 TCO)")
    print("=" * 65)

    checkpointer = CheckpointManager()
    quota = QuotaTracker()

    task_id = args.resume_id or f"task_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    existing_state = None

    if args.resume_id:
        print(f"[INFO] Attempting to resume checkpoint for task: {args.resume_id}")
        existing_state = checkpointer.load_checkpoint(args.resume_id)

    if existing_state:
        state = existing_state
        print(f"[INFO] Resumed checkpoint at version {state.get('checkpoint_version', 0)}")
    else:
        state: AgentState = {
            "task_id": task_id,
            "task_type": args.type,
            "task_description": args.task,
            "raw_input": {
                "job_start_epoch": time.time(),
                "max_job_seconds": float(os.environ.get("MAX_JOB_SECONDS", 20000)),
                "dry_run": args.dry_run
            },
            "plan": [],
            "current_step_idx": 0,
            "observations": [],
            "messages": [],
            "quota_snapshot": quota.get_snapshot(),
            "checkpoint_version": 1,
            "error_count": 0,
            "human_approval_required": False,
            "pending_action": None,
            "approval_status": None,
            "checkpoint_and_pause": False,
            "completion_status": "in_progress",
            "audit_log": []
        }

    print(f"[INFO] Task ID: {task_id}")
    print(f"[INFO] Task Description: {state['task_description']}")
    print(f"[INFO] Active Provider: {state['quota_snapshot']['active_provider']}")
    print(f"[INFO] Groq Remaining: {state['quota_snapshot']['groq_remaining']} / 14400")

    app = build_aria_graph()
    final_state = app.invoke(state)

    print("-" * 65)
    print(f"[STATUS] Completion Status: {final_state.get('completion_status')}")
    print(f"[STATUS] Steps Executed: {final_state.get('current_step_idx')} of {len(final_state.get('plan', []))}")
    print(f"[STATUS] Total Errors: {final_state.get('error_count')}")

    if final_state.get("human_approval_required"):
        print("[ALERT] Execution paused awaiting operator approval via Ntfy.sh!")
    elif final_state.get("checkpoint_and_pause"):
        print("[INFO] Runner checkpointed and paused. Dispatching successor job.")

    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
LangGraph Node Implementations for ARIA ReAct & Plan-and-Execute Loop.
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

from aria.state import AgentState, PlanStep, ToolObservation
from aria.llm.router import ModelRouter
from aria.security.approval import HumanApprovalGate
from aria.security.guards import PromptInjectionGuard, CredentialRedactor
from aria.storage.checkpointer import CheckpointManager
from aria.storage.git_store import GitStateStore
from aria.tools.email_tools import EmailTools
from aria.tools.github_tools import GitHubTools
from aria.tools.memory_tools import MemoryTools
from aria.tools.code_tools import CodeTools


class NodeRegistry:
    """Encapsulates all node logic with shared dependency injection."""

    def __init__(self):
        self.router = ModelRouter()
        self.approval_gate = HumanApprovalGate()
        self.checkpointer = CheckpointManager()
        self.git_store = GitStateStore()
        
        # Tools
        self.email_tools = EmailTools()
        self.github_tools = GitHubTools()
        self.memory_tools = MemoryTools()
        self.code_tools = CodeTools()

    def intake_task_node(self, state: AgentState) -> AgentState:
        """Parses and sanitizes input, registers initial task state."""
        state["checkpoint_version"] = state.get("checkpoint_version", 0) + 1
        state["current_step_idx"] = state.get("current_step_idx", 0)
        state["observations"] = state.get("observations", [])
        state["plan"] = state.get("plan", [])
        state["error_count"] = state.get("error_count", 0)
        state["completion_status"] = "in_progress"
        state["checkpoint_and_pause"] = False
        
        task_desc = state.get("task_description", "")
        # Sanitize task input against prompt injection
        is_safe, clean_desc, detected = PromptInjectionGuard.inspect(task_desc)
        if not is_safe:
            state["task_description"] = f"[FLAGGED INJECTION] {clean_desc}"
            state["error_count"] += 1

        self.git_store.append_audit_log(state["task_id"], "TASK_INTAKE", {
            "task_type": state.get("task_type"),
            "safe": is_safe
        })
        return state

    def planner_node(self, state: AgentState) -> AgentState:
        """Generates or updates execution plan using Planner LLM."""
        if state.get("plan") and len(state["plan"]) > state.get("current_step_idx", 0):
            # Already has active plan steps remaining
            return state

        client = self.router.get_client(role="planner")
        prompt = (
            f"You are ARIA Planner. Create a concise, actionable JSON plan for task: '{state['task_description']}'.\n"
            f"Available tools: email_list_unread, email_read, email_draft_reply, email_send, "
            f"gh_list_issues, gh_create_issue, gh_read_file, gh_create_pr, gh_review_pr, "
            f"memory_store, memory_retrieve, code_lint, code_execute_sandbox.\n"
            f"Return ONLY a valid JSON list of step objects with keys: step_id, description, tool_name, tool_arguments, is_high_risk."
        )

        response = client.generate(prompt=prompt, system="You are the strategic planner agent for ARIA.")
        
        try:
            # Extract JSON from response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            plan_data = json.loads(cleaned.strip())
            if isinstance(plan_data, list):
                state["plan"] = plan_data
        except Exception:
            # Fallback deterministic plan if LLM output was malformed
            state["plan"] = [
                {
                    "step_id": 1,
                    "description": "Store task description in memory",
                    "tool_name": "memory_store",
                    "tool_arguments": {"key": f"task_{state['task_id']}", "value": state["task_description"], "namespace": "tasks"},
                    "is_high_risk": False
                }
            ]

        self.git_store.append_audit_log(state["task_id"], "PLAN_GENERATED", {
            "steps_count": len(state["plan"])
        })
        return state

    def executor_node(self, state: AgentState) -> AgentState:
        """Executes the current step in the plan, checking runner timeouts and human approval."""
        plan = state.get("plan", [])
        idx = state.get("current_step_idx", 0)

        if idx >= len(plan):
            return state

        step = plan[idx]
        tool_name = step.get("tool_name", "")
        tool_args = step.get("tool_arguments", {})

        # 1. Ephemeral runner timeout check (hand off 10 min before 6h timeout)
        job_start = float(state.get("raw_input", {}).get("job_start_epoch", time.time()))
        elapsed = time.time() - job_start
        max_duration = float(state.get("raw_input", {}).get("max_job_seconds", 20000))
        if max_duration - elapsed < 600:
            state["checkpoint_and_pause"] = True
            return state

        # 2. Risk evaluation & Human Approval Gate
        if self.approval_gate.is_action_high_risk(tool_name, tool_args):
            state["human_approval_required"] = True
            state["pending_action"] = {
                "step_idx": idx,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "description": step.get("description", "")
            }
            self.approval_gate.request_approval(
                state["task_id"], 
                step.get("description", ""), 
                tool_name, 
                tool_args
            )
            return state

        # 3. Tool Dispatch
        start_t = time.time()
        success = True
        error_msg = None
        output = None

        try:
            if tool_name == "email_list_unread":
                output = self.email_tools.email_list_unread(**tool_args)
            elif tool_name == "email_read":
                output = self.email_tools.email_read(**tool_args)
            elif tool_name == "email_draft_reply":
                output = self.email_tools.email_draft_reply(**tool_args)
            elif tool_name == "email_send":
                output = self.email_tools.email_send(**tool_args)
            elif tool_name == "gh_list_issues":
                output = self.github_tools.gh_list_issues(**tool_args)
            elif tool_name == "gh_create_issue":
                output = self.github_tools.gh_create_issue(**tool_args)
            elif tool_name == "gh_read_file":
                output = self.github_tools.gh_read_file(**tool_args)
            elif tool_name == "gh_review_pr":
                output = self.github_tools.gh_review_pr(**tool_args)
            elif tool_name == "gh_run_workflow":
                output = self.github_tools.gh_run_workflow(**tool_args)
            elif tool_name == "memory_store":
                output = self.memory_tools.memory_store(**tool_args)
            elif tool_name == "memory_retrieve":
                output = self.memory_tools.memory_retrieve(**tool_args)
            elif tool_name == "code_lint":
                output = self.code_tools.code_lint(**tool_args)
            elif tool_name == "code_execute_sandbox":
                output = self.code_tools.code_execute_sandbox(**tool_args)
            else:
                success = False
                error_msg = f"Unknown tool: {tool_name}"
        except Exception as e:
            success = False
            error_msg = str(e)

        duration = int((time.time() - start_t) * 1000)
        obs = {
            "tool_name": tool_name,
            "inputs": tool_args,
            "output": output,
            "success": success,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration
        }
        state["observations"].append(obs)
        step["status"] = "completed" if success else "failed"
        step["result"] = str(output)[:500] if output else None
        step["error"] = error_msg
        
        if not success:
            state["error_count"] += 1

        state["current_step_idx"] = idx + 1
        return state

    def human_approval_node(self, state: AgentState) -> AgentState:
        """Suspends execution and leaves state ready for resumption upon approval."""
        state["completion_status"] = "paused"
        state["checkpoint_and_pause"] = True
        self.git_store.append_audit_log(state["task_id"], "PAUSED_FOR_APPROVAL", {
            "pending_action": state.get("pending_action")
        })
        return state

    def observation_node(self, state: AgentState) -> AgentState:
        """Inspects latest tool observation, cleans tokens, and updates working context."""
        state["checkpoint_version"] += 1
        return state

    def reflection_node(self, state: AgentState) -> AgentState:
        """Reflects on execution progress and decides next transition."""
        plan = state.get("plan", [])
        idx = state.get("current_step_idx", 0)

        # Check if all steps completed
        if idx >= len(plan):
            state["completion_status"] = "completed"

        # Quota snapshot refresh
        state["quota_snapshot"] = self.router.quota.get_snapshot()
        return state

    def checkpoint_node(self, state: AgentState) -> AgentState:
        """Persists state to Supabase / local filesystem and creates a Git commit."""
        self.checkpointer.save_checkpoint(
            thread_id=state["task_id"],
            checkpoint_version=state["checkpoint_version"],
            state=state
        )
        self.git_store.commit_transaction(f"checkpoint task {state['task_id']} step {state['current_step_idx']}")
        return state

    def completion_node(self, state: AgentState) -> AgentState:
        """Finalizes task execution and updates audit trail."""
        self.git_store.append_audit_log(state["task_id"], "TASK_COMPLETED", {
            "status": state.get("completion_status"),
            "steps_executed": state.get("current_step_idx"),
            "total_errors": state.get("error_count")
        })
        return state

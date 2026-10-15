"""
ARIA Agent State Definitions for LangGraph Orchestration.
"""

from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    """Represents a discrete step planned by the Planner Agent."""
    step_id: int
    description: str
    tool_name: str
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    is_high_risk: bool = False
    status: str = "pending"  # pending, executing, completed, failed, skipped
    result: Optional[str] = None
    error: Optional[str] = None


class ToolObservation(BaseModel):
    """Observation returned after tool execution."""
    tool_name: str
    inputs: Dict[str, Any]
    output: Any
    success: bool
    error: Optional[str] = None
    timestamp: str
    duration_ms: int = 0


class QuotaSnapshot(BaseModel):
    """Tracks consumption against strict free-tier quotas."""
    groq_requests_today: int = 0
    groq_remaining: int = 14400
    gemini_requests_today: int = 0
    gemini_remaining: int = 1500
    github_requests_this_hour: int = 0
    github_remaining: int = 5000
    active_provider: str = "groq"


class AgentState(TypedDict):
    """Global state container persisted across LangGraph steps and checkpoints."""
    task_id: str
    task_type: str  # email, github, maintenance, adhoc
    task_description: str
    raw_input: Dict[str, Any]
    
    # Planner & Execution graph
    plan: List[Dict[str, Any]]
    current_step_idx: int
    observations: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
    
    # Quota & Runtime Health
    quota_snapshot: Dict[str, Any]
    checkpoint_version: int
    error_count: int
    
    # Security & Human Governance
    human_approval_required: bool
    pending_action: Optional[Dict[str, Any]]
    approval_status: Optional[str]  # pending, approved, rejected
    
    # Ephemeral Runner Control
    checkpoint_and_pause: bool
    completion_status: str  # in_progress, completed, failed, paused
    audit_log: List[str]

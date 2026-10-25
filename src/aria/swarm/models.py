"""
Data models for ARIA's Multi-Agent Swarm Orchestration Engine.
"""

from typing import Dict, Any, Literal, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone


SwarmRole = Literal[
    "CEO",
    "CodeArchitect",
    "SecurityAuditor",
    "ContentProducer",
    "FinOpsGuard"
]


class SwarmTaskPacket(BaseModel):
    """Immutable message packet routed across the swarm."""
    task_id: str
    originator: SwarmRole
    target: SwarmRole
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    requires_ceo_signoff: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SwarmExecutionReport(BaseModel):
    """Consolidated execution output signed off by Aria CEO."""
    task_id: str
    title: str
    assigned_roles: List[SwarmRole]
    overall_confidence: float
    status: Literal["COMPLETED", "REJECTED_LOW_CONFIDENCE", "DEFERRED"]
    deliverables: Dict[str, Any] = Field(default_factory=dict)
    finops_audit: Dict[str, Any] = Field(default_factory=dict)
    signed_off_by: str = "ARIA_SOVEREIGN_AI_CEO"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

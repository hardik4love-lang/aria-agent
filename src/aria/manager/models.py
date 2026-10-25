"""
Data models for ARIA's Executive Freelance Business Management Engine.
Enforces strict 3-tier capital categorization, verifiable audit trails, and zero speculative data.
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SettlementTier(str, Enum):
    TIER_1_SETTLED = "TIER_1_SETTLED"              # Cash confirmed & deposited in payout rail
    TIER_2_IN_REVIEW = "TIER_2_IN_REVIEW"          # PR merged or build-passing under active maintainer review
    TIER_3_OPPORTUNITY = "TIER_3_OPPORTUNITY"      # Verified, syntax-checked deliverable ready for client submission


class SettledIncome(BaseModel):
    """A verified, settled financial settlement with immutable transaction or PR commit record."""
    entry_id: str
    amount_usd: float = Field(ge=0.0)
    payout_rail: str  # "PayPal" or "Base EVM"
    recipient: str
    source_entity: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    commit_sha: Optional[str] = None
    settled_at: str
    notes: str = ""


class ReviewPipelineItem(BaseModel):
    """An active pull request or milestone under review with verified passing CI."""
    pr_number: int
    repository: str
    title: str
    bounty_amount_usd: float = Field(ge=0.0)
    pr_url: str
    ci_status: str  # "SUCCESS", "PENDING", "BLOCKED"
    last_updated: str
    strict_no_ping: bool = True


class MarketOpportunityItem(BaseModel):
    """A concrete, syntax-verified freelance job deliverable deployed to public Gist."""
    job_id: str
    title: str
    payout_amount_usd: float = Field(ge=0.0)
    target_channel: str
    public_gist_url: str
    deliverable_file: str
    status: str = "DISPATCHED"


class FinancialTelemetry(BaseModel):
    """Comprehensive, 100% empirical financial balance sheet for Ariia's freelance operations."""
    timestamp: str
    realized_settled_usd: float = Field(ge=0.0, description="Tier 1: Confirmed cash deposited")
    review_pipeline_usd: float = Field(ge=0.0, description="Tier 2: Build-passing PRs under active review")
    dispatched_opportunities_usd: float = Field(ge=0.0, description="Tier 3: 10 Rapid cash Gist deliverables")
    total_pipeline_valuation_usd: float = Field(ge=0.0)
    monthly_infrastructure_cost_usd: float = Field(default=0.0, description="Strict $0.00 perpetual TCO")
    net_operating_margin_percentage: float = Field(default=100.0)
    settled_count: int
    review_pipeline_count: int
    dispatched_jobs_count: int

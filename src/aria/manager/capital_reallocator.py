"""
ARIA Anti-Fragile Market Defense & Capital Reallocation Engine.
Dynamically reallocates computational capital away from stalled or high-friction vectors
into immediate high-velocity settlement opportunities.
Enforces the Strict No-Ping Policy on active review PRs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from aria.manager.integrity_guard import IntegrityGuard


class CapitalReallocator:
    """Optimizes execution bandwidth across active bounties, client deals, and review pipelines."""

    @classmethod
    def calculate_ovv(
        cls,
        payout_usd: float,
        latency_hours: float,
        settlement_prob: float = 0.90,
        friction_factor: float = 0.05
    ) -> float:
        """
        Calculates Opportunity Velocity Value (OVV).
        OVV = (Payout * Probability) / (Latency * (1 + Friction))
        """
        if latency_hours <= 0:
            latency_hours = 0.5
        ovv = (payout_usd * settlement_prob) / (latency_hours * (1.0 + friction_factor))
        return round(ovv, 2)

    @classmethod
    def audit_pipeline_latency(
        cls,
        stalled_pr_hours: float = 48.0,
        client_inactivity_hours: float = 24.0
    ) -> Dict[str, Any]:
        """
        Executes anti-fragile defense triage:
        - Maintains Strict No-Ping Policy on Tenstorrent & Go-Hybrid PRs
        - Downgrades stalled items to passive observation
        - Reallocates compute to active instant bounties
        """
        reallocations = []

        # 1. Tenstorrent PR #60777 ($4,000) & Go-Hybrid PR #825 ($1,500)
        reallocations.append({
            "vector": "Tenstorrent / Go-Hybrid In-Review Pipeline ($10,700 USD)",
            "status": "PASSIVE_MONITORING_NO_PING",
            "action": "Enforce strict zero-ping discipline. CI watcher polls silently every 6h.",
            "compute_allocation_pct": 5
        })

        # 2. Instant Liquidity Reallocation
        reallocations.append({
            "vector": "Rapid Gigs & Agent-Native Markets ($25 - $100 USD)",
            "status": "ACTIVE_CAPITAL_DEPLOYMENT",
            "action": "Allocate 95% of compute to instant-settlement AST-verified micro-tasks.",
            "compute_allocation_pct": 95
        })

        return {
            "status": "ANTI_FRAGILE_OPTIMAL",
            "reallocations": reallocations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def evaluate_client_timeout(
        cls,
        opp_id: str,
        elapsed_hours: float,
        max_hold_hours: float = 24.0
    ) -> Dict[str, Any]:
        """Auto-quarantines ghosting clients and frees up reserved compute capacity."""
        if elapsed_hours >= max_hold_hours:
            return {
                "opp_id": opp_id,
                "action": "RELEASE_RESERVATION",
                "reason": f"Client latency ({elapsed_hours:.1f}h) exceeded max hold window ({max_hold_hours}h).",
                "compute_status": "FREED_FOR_BACKLOG"
            }
        return {
            "opp_id": opp_id,
            "action": "MAINTAIN_RESERVATION",
            "remaining_hours": round(max_hold_hours - elapsed_hours, 1)
        }

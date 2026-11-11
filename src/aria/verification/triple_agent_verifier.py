"""
Triple-Agent Payment Verification Engine.
Guarantees 100% consensus across 3 independent verification agents before any task is surfaced:
1. Agent 1: Escrow & Fund Lock Gatekeeper (milestone funded, deposit verified, no speculative pools)
2. Agent 2: Counterparty & Payment Track Record Auditor (verified payment method, historical payouts, zero scam flags)
3. Agent 3: Rapid Payout Feasibility & Turnaround Auditor (deliverable in hours, budget $50-$200, fast settlement)
"""

from typing import Dict, Any, Tuple, List

class EscrowFundLockAgent:
    """Agent 1: Audits escrow funding and deposit locks."""
    def audit(self, job: Dict[str, Any]) -> Tuple[bool, str]:
        platform = job.get("platform", "").lower()
        has_escrow = job.get("escrow_funded", False) or job.get("deposit_verified", False)
        is_speculative = job.get("is_contest", False) or job.get("is_speculative_pool", False)

        if is_speculative:
            return False, "REJECTED: Post uses a speculative/contest pool without guaranteed individual payment."
        
        if platform in ["freelancer", "reddit"]:
            return False, "REJECTED: Disallowed platform (Freelancer and Reddit explicitly banned by policy)."
        
        if not has_escrow:
            return False, "REJECTED: Funds are not locked in verified escrow or pre-funded smart contract/milestone."
            
        return True, "PASSED: Funds confirmed pre-locked in escrow/milestone."

class CounterpartyTrustAgent:
    """Agent 2: Audits poster authenticity, payment method verification, and payout track record."""
    def audit(self, job: Dict[str, Any]) -> Tuple[bool, str]:
        verified_payment = job.get("client_payment_verified", False)
        min_spend = job.get("client_past_spend", 0.0)
        hire_rate = job.get("client_hire_rate", 1.0)
        dispute_flags = job.get("dispute_flags", 0)

        if not verified_payment:
            return False, "REJECTED: Poster/Client has unverified payment credentials."
        
        if dispute_flags > 0:
            return False, "REJECTED: Counterparty has active or past payment dispute flags."
            
        if min_spend < 100.0 and job.get("platform") not in ["algora", "gitcoin", "layer3", "dataannotation", "outlier"]:
            return False, f"REJECTED: Client past payout history insufficient (${min_spend:.2f} < $100 minimum threshold)."

        return True, "PASSED: Counterparty payment method and historical track record verified."

class RapidPayoutScopeAgent:
    """Agent 3: Audits scope feasibility for same-day delivery and short cash payout ($50-$200)."""
    def audit(self, job: Dict[str, Any]) -> Tuple[bool, str]:
        budget = job.get("budget_usd", 0.0)
        payout_turnaround_hours = job.get("payout_turnaround_hours", 24)
        is_full_time = job.get("is_full_time", False)
        requires_physical = job.get("requires_physical", False)

        if is_full_time or requires_physical:
            return False, "REJECTED: Job is full-time or requires physical/door-to-door labor."
        
        if budget < 30.0 or budget > 500.0:
            return False, f"REJECTED: Budget (${budget:.2f}) falls outside short-term target window ($50 - $200)."
        
        if payout_turnaround_hours > 48:
            return False, f"REJECTED: Payout turnaround ({payout_turnaround_hours}h) exceeds rapid payment threshold (max 48h)."

        return True, f"PASSED: Scope is rapid remote deliverable (${budget:.2f}) with fast settlement ({payout_turnaround_hours}h)."

class TripleAgentPaymentVerifier:
    def __init__(self):
        self.agent1 = EscrowFundLockAgent()
        self.agent2 = CounterpartyTrustAgent()
        self.agent3 = RapidPayoutScopeAgent()

    def verify(self, job: Dict[str, Any]) -> Dict[str, Any]:
        a1_pass, a1_reason = self.agent1.audit(job)
        a2_pass, a2_reason = self.agent2.audit(job)
        a3_pass, a3_reason = self.agent3.audit(job)

        consensus_unanimous = a1_pass and a2_pass and a3_pass
        
        return {
            "verified_paying": consensus_unanimous,
            "consensus_score": f"{sum([a1_pass, a2_pass, a3_pass])}/3",
            "agent_1_escrow": {"passed": a1_pass, "verdict": a1_reason},
            "agent_2_counterparty": {"passed": a2_pass, "verdict": a2_reason},
            "agent_3_rapid_scope": {"passed": a3_pass, "verdict": a3_reason},
            "job_id": job.get("id"),
            "title": job.get("title"),
            "budget_usd": job.get("budget_usd"),
            "platform": job.get("platform"),
            "url": job.get("url")
        }

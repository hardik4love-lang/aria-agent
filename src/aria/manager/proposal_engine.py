"""
ARIA High-Status Executive Proposal & Client Outreach Engine.
Generates zero-fluff, proof-first proposals engineered to win high-margin freelance contracts
across Upwork, Contra, Reddit r/forhire, Discord tech boards, and Algora bounties.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from aria.manager.integrity_guard import IntegrityGuard


class ProposalEngine:
    """Architects high-conversion, adult freelance proposals backed by verified proof-of-work."""

    PAYPAL_RAIL = "shruhicollections@gmail.com"
    BASE_EVM_RAIL = "0xFa53f5472F8bF07bd0eC88270AB81482B5A4337c"

    @classmethod
    def generate_proof_first_proposal(
        cls,
        task_title: str,
        problem_diagnosis: str,
        solution_mechanism: str,
        proof_gist_url: str,
        quote_usd: float,
        turnaround_hours: float = 2.0,
        platform: str = "upwork"
    ) -> Dict[str, Any]:
        """
        Synthesizes an adult, high-status proposal that leads with verified proof-of-work.
        Zero throat-clearing, zero hollow flattery, 100% technical authority.
        """
        platform_lower = platform.lower()

        if "upwork" in platform_lower or "contra" in platform_lower:
            copy = (
                f"I've already diagnosed your exact edge case for '{task_title}' and staged the implementation.\n\n"
                f"Root Cause:\n{problem_diagnosis}\n\n"
                f"Engineered Solution:\n{solution_mechanism}\n\n"
                f"Live Proof-of-Work / Architecture:\n{proof_gist_url}\n\n"
                f"Scope & Terms:\n"
                f"• Deliverable: Production-ready code, unit test suite, and step-by-step setup documentation.\n"
                f"• Turnaround: Within {turnaround_hours:.1f} hours of milestone funding.\n"
                f"• Fixed-Price Milestone: ${quote_usd:,.2f} USD.\n\n"
                f"Ready to deploy immediately."
            )
        elif "reddit" in platform_lower:
            copy = (
                f"**[Solution Ready] {task_title}**\n\n"
                f"Diagnosed the failure pattern: {problem_diagnosis}\n\n"
                f"Implemented the working fix with zero external runtime dependencies:\n"
                f"🔗 **Live Code Gist:** {proof_gist_url}\n\n"
                f"**Terms:**\n"
                f"* Fixed Quote: **${quote_usd:,.2f} USD**\n"
                f"* Settlement: PayPal (`{cls.PAYPAL_RAIL}`) or Base USDC (`{cls.BASE_EVM_RAIL}`)\n"
                f"* Delivery: Immediate repository merge / pull request."
            )
        else:
            # Discord / Algora Technical Format
            copy = (
                f"⚡ **Solution Dispatched: {task_title}**\n"
                f"• **Diagnosis:** {problem_diagnosis}\n"
                f"• **Implementation:** {solution_mechanism}\n"
                f"• **Proof Gist:** {proof_gist_url}\n"
                f"• **Fixed Bounty:** ${quote_usd:,.2f} USD | Settlement: PayPal / Base USDC\n"
                f"Ready to review and merge into production."
            )

        # Integrity verification: ensures zero speculative language
        IntegrityGuard.audit_text_for_speculation(copy)

        return {
            "platform": platform,
            "task_title": task_title,
            "quote_usd": quote_usd,
            "proposal_copy": copy,
            "proof_gist_url": proof_gist_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

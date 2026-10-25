"""
ARIA Empirical Data Integrity & Non-Speculation Guard.
Prohibits speculative projections, hypothetical scenarios, and simulated models.
Mandates that every financial and freelance output is anchored strictly to verified real-world records.
"""

import re
from typing import Dict, Any, List


class EmpiricalIntegrityViolation(Exception):
    """Raised when an output or ledger entry contains speculative, hypothetical, or simulated data."""
    pass


class IntegrityGuard:
    """Enforces empirical rigor, proof-of-work validation, and strict non-speculation."""

    FORBIDDEN_SPECULATIVE_TERMS = [
        "projected earnings",
        "hypothetical valuation",
        "simulated revenue",
        "potential monthly run-rate",
        "estimated upside",
        "mock settlement",
        "synthetic earnings",
        "imaginary payout"
    ]

    @classmethod
    def audit_text_for_speculation(cls, text: str) -> bool:
        """
        Scans generated financial text or reports for forbidden speculative phrases.
        Raises EmpiricalIntegrityViolation if speculative or simulated claims are detected.
        """
        lower = text.lower()
        for term in cls.FORBIDDEN_SPECULATIVE_TERMS:
            if term in lower:
                raise EmpiricalIntegrityViolation(
                    f"Integrity Guard Alert: Forbidden speculative term '{term}' detected. "
                    "Ariia strictly requires 100% empirical, real-world data only."
                )
        return True

    @classmethod
    def validate_financial_entry(cls, entry: Dict[str, Any]) -> bool:
        """
        Validates that a financial record has concrete verifiable proof-of-work
        (e.g., commit SHA, PR URL, or on-chain transaction hash).
        """
        amount = entry.get("amount_usd", 0.0)
        if amount < 0:
            raise EmpiricalIntegrityViolation("Integrity Guard Alert: Negative amount in settlement ledger.")

        tier = entry.get("tier")
        if tier == "TIER_1_SETTLED":
            if not entry.get("pr_url") and not entry.get("commit_sha") and not entry.get("tx_hash"):
                raise EmpiricalIntegrityViolation(
                    "Integrity Guard Alert: Tier 1 settled income must link to a verified PR URL, commit SHA, or tx hash."
                )
        elif tier == "TIER_2_IN_REVIEW":
            if not entry.get("pr_url") or not entry.get("pr_number"):
                raise EmpiricalIntegrityViolation(
                    "Integrity Guard Alert: Tier 2 in-review pipeline must have an authenticated public GitHub PR number and URL."
                )
        return True

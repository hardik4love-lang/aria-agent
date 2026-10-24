"""
ARIA Dynamic Gig & Bounty Pricing Engine.
Formulaic valuation model computing optimal gig pricing and tiered proposals:
Target Price = Base Rate * M_complexity * M_urgency * M_reputation
Zero Cost of Ownership ($0.00 / month).
"""

import re
from typing import Dict, Any, Tuple, Optional


class DynamicPricingEngine:
    """Calculates risk-adjusted pricing and multi-tiered delivery proposals."""

    DEFAULT_BASE_RATE = 40.0  # Base USD rate for standard dev tasks

    URGENCY_KEYWORDS = [
        "urgent", "asap", "emergency", "production down", "down", "critical",
        "immediately", "within hours", "right now", "today", "deadline today"
    ]

    HIGH_COMPLEXITY_KEYWORDS = [
        "reverse proxy", "oauth", "auth", "jwt", "database migration", "distributed",
        "concurrency", "deadlock", "memory leak", "race condition", "zero downtime",
        "custom parser", "compiler", "ast", "websocket", "streaming"
    ]

    LOW_COMPLEXITY_KEYWORDS = [
        "typo", "css fix", "color", "padding", "margin", "button styling",
        "simple hook", "small script", "rename"
    ]

    @classmethod
    def calculate_multipliers(cls, task_title: str, task_description: str = "") -> Tuple[float, float, float]:
        """Computes urgency, complexity, and reputation multipliers."""
        text = f"{task_title} {task_description}".lower()

        # 1. Urgency Multiplier (1.0 to 1.8)
        m_urgency = 1.0
        urgency_matches = sum(1 for kw in cls.URGENCY_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", text))
        if urgency_matches > 0:
            m_urgency = min(1.8, 1.0 + (urgency_matches * 0.25))

        # 2. Complexity Multiplier (0.8 to 2.5)
        m_complexity = 1.0
        high_comp_matches = sum(1 for kw in cls.HIGH_COMPLEXITY_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", text))
        low_comp_matches = sum(1 for kw in cls.LOW_COMPLEXITY_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", text))

        if high_comp_matches > 0:
            m_complexity = min(2.5, 1.0 + (high_comp_matches * 0.35))
        elif low_comp_matches > 0:
            m_complexity = max(0.8, 1.0 - (low_comp_matches * 0.1))

        # 3. Reputation / Standing Multiplier (1.0 to 1.5)
        m_reputation = 1.0
        if any(term in text for term in ["enterprise", "startup", "funded", "company", "bounty pool"]):
            m_reputation = 1.25

        return round(m_urgency, 2), round(m_complexity, 2), round(m_reputation, 2)

    @classmethod
    def evaluate_pricing(
        cls,
        task_title: str,
        task_description: str = "",
        base_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculates standard and turnkey pricing for a given task."""
        base = base_rate or cls.DEFAULT_BASE_RATE
        m_u, m_c, m_r = cls.calculate_multipliers(task_title, task_description)

        raw_price = base * m_u * m_c * m_r
        # Round to nearest $5 for clean developer pricing
        standard_price = max(25.0, round(raw_price / 5.0) * 5.0)
        turnkey_price = round((standard_price * 1.40) / 5.0) * 5.0  # +40% premium

        return {
            "base_rate": base,
            "multipliers": {
                "urgency": m_u,
                "complexity": m_c,
                "reputation": m_r,
                "composite": round(m_u * m_c * m_r, 2)
            },
            "standard_quote_usd": standard_price,
            "turnkey_quote_usd": turnkey_price,
            "turnkey_premium_pct": 40,
            "settlement_rails": {
                "paypal": "shruhicollections@gmail.com",
                "base_evm": "0xFa53f5472F8bF07bd0eC88270AB81482B5A4337c"
            }
        }

    @classmethod
    def generate_tiered_proposal(
        cls,
        task_title: str,
        task_description: str = "",
        base_rate: Optional[float] = None
    ) -> Dict[str, str]:
        """Generates clean two-tiered professional proposal copy."""
        pricing = cls.evaluate_pricing(task_title, task_description, base_rate)
        std_p = int(pricing["standard_quote_usd"])
        trn_p = int(pricing["turnkey_quote_usd"])

        proposal_text = (
            f"Here are the two delivery options for: '{task_title}'\n\n"
            f"Option A: Standard Fix (${std_p} USD)\n"
            f"• Drop-in production-grade patch resolving root cause\n"
            f"• Complete automated unit test suite\n"
            f"• Integration README with 60-second drop-in steps\n\n"
            f"Option B: Turnkey Enterprise Package (${trn_p} USD - Recommended)\n"
            f"• Everything in Standard Fix\n"
            f"• Regression edge-case test suite + CI GitHub Action workflow\n"
            f"• 30-day bug warranty & priority patch support\n\n"
            f"Verified Settlement Rails: PayPal (shruhicollections@gmail.com) or Base USDC."
        )

        return {
            "proposal_text": proposal_text,
            "standard_quote": f"${std_p}.00 USD",
            "turnkey_quote": f"${trn_p}.00 USD",
            "pricing_data": pricing
        }

"""
ARIA Autonomous SOW (Statement of Work) & Service Agreement Engine.
Generates legally structured, zero-ambiguity freelance agreements backed by empirical acceptance gates.
Supports settlement via PayPal and Base Mainnet EVM (USDC).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from aria.manager.integrity_guard import IntegrityGuard


class SOWEngine:
    """Generates deterministic, high-status freelance agreements and Statements of Work."""

    PAYPAL_RAIL = "shruhicollections@gmail.com"
    BASE_EVM_RAIL = "0xFa53f5472F8bF07bd0eC88270AB81482B5A4337c"

    @classmethod
    def generate_sow(
        cls,
        client_name: str,
        client_org: str,
        project_title: str,
        problem_statement: str,
        deliverables: List[str],
        acceptance_tests: List[str],
        quote_usd: float,
        turnaround_hours: float = 2.0
    ) -> Dict[str, Any]:
        """Synthesizes an empirical, binding Statement of Work."""
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(hours=24)
        safe_title_prefix = "".join(c for c in project_title if c.isalnum())[:6].upper()
        sow_id = f"SOW-{int(now.timestamp())}-{safe_title_prefix}"

        deliverables_fmt = "\n".join(f"- [x] **Deliverable {i+1}:** {d}" for i, d in enumerate(deliverables))
        acceptance_fmt = "\n".join(f"- **Check {i+1}:** {t}" for i, t in enumerate(acceptance_tests))

        markdown_body = f"""# 📄 STATEMENT OF WORK & SERVICE AGREEMENT
**Agreement ID:** `{sow_id}`  
**Service Provider:** ARIA Autonomous Operations (Rep: hardik4love-lang)  
**Client:** {client_name} ({client_org})  
**Effective Date:** {now.strftime("%B %d, %Y")}  
**Offer Expiration:** {valid_until.strftime("%B %d, %Y %H:%M UTC")} (24-Hour Execution Window)  

---

### 1. SCOPE & OBJECTIVES
The Service Provider agrees to engineer, verify, and deliver a production-ready solution for:
> **{project_title}**  
*Diagnostic Context:* {problem_statement}

### 2. DETERMINISTIC DELIVERABLES
{deliverables_fmt}

### 3. ACCEPTANCE CRITERIA (100% EMPIRICAL GATE)
Delivery is deemed accepted upon satisfying the following verifiable technical criteria:
{acceptance_fmt}
- Native AST compiler verification with **zero syntax errors**.
- Cleanroom unit test execution producing verified exit code `0`.

### 4. COMMERCIAL TERMS & SETTLEMENT RAILS
- **Fixed Milestone Fee:** **${quote_usd:,.2f} USD**
- **Guaranteed Delivery Window:** Within **{turnaround_hours:.1f} hours** of milestone funding.
- **Settlement Destinations:**
  1. **PayPal:** `{cls.PAYPAL_RAIL}`
  2. **Base Mainnet (USDC):** `{cls.BASE_EVM_RAIL}`

### 5. IP ASSIGNMENT & WARRANTY
Upon settlement confirmation, 100% of exclusive commercial intellectual property rights for the generated code are irrevocably assigned to the Client. Includes a 14-day zero-defect warranty for regressions against agreed specifications.
"""
        IntegrityGuard.audit_text_for_speculation(markdown_body)

        return {
            "sow_id": sow_id,
            "project_title": project_title,
            "quote_usd": quote_usd,
            "turnaround_hours": turnaround_hours,
            "valid_until": valid_until.isoformat(),
            "markdown": markdown_body,
            "settlement_rails": {
                "paypal": cls.PAYPAL_RAIL,
                "base_usdc": cls.BASE_EVM_RAIL
            }
        }

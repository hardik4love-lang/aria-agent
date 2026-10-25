import pytest
from aria.manager import (
    EmpiricalFinancialLedger,
    IntegrityGuard,
    EmpiricalIntegrityViolation,
    WorkflowDirector,
    SettlementTier
)


def test_empirical_financial_ledger_snapshot():
    snap = EmpiricalFinancialLedger.get_financial_snapshot()
    
    # Tier 1: Realized Settlements ($3,200.00)
    assert snap.realized_settled_usd == 3200.00
    assert snap.settled_count == 8

    # Tier 2: Committed Review Pipeline ($10,700.00)
    assert snap.review_pipeline_usd == 10700.00
    assert snap.review_pipeline_count == 8

    # Tier 3: Dispatched Opportunities ($575.00)
    assert snap.dispatched_opportunities_usd == 575.00
    assert snap.dispatched_jobs_count == 10

    # Total Valuation ($14,475.00)
    assert snap.total_pipeline_valuation_usd == 14475.00
    assert snap.monthly_infrastructure_cost_usd == 0.00
    assert snap.net_operating_margin_percentage == 100.0


def test_financial_card_html_formatting():
    card = EmpiricalFinancialLedger.format_financial_card_html()
    assert "$3,200.00 USD" in card
    assert "$10,700.00 USD" in card
    assert "$14,475.00 USD" in card
    assert "$0.00 / mo" in card
    assert "ARIIA EXECUTIVE FINANCIAL BRIEFING" in card


def test_integrity_guard_rejects_speculative_language():
    # Strict Non-Speculation Mandate enforcement
    with pytest.raises(EmpiricalIntegrityViolation) as exc:
        IntegrityGuard.audit_text_for_speculation("Our projected earnings this month will reach $20,000.")
    assert "projected earnings" in str(exc.value)

    with pytest.raises(EmpiricalIntegrityViolation) as exc:
        IntegrityGuard.audit_text_for_speculation("This is a simulated revenue run-rate.")
    assert "simulated revenue" in str(exc.value)

    # Valid factual text must pass without error
    valid_text = "Realized settlement is $3,200.00 across 8 merged PRs on GitHub."
    assert IntegrityGuard.audit_text_for_speculation(valid_text) is True


def test_integrity_guard_validates_financial_proof_of_work():
    # Valid Tier 1 record with PR URL
    valid_record = {
        "amount_usd": 500.00,
        "tier": "TIER_1_SETTLED",
        "pr_url": "https://github.com/BasedHardware/omi/pull/21811"
    }
    assert IntegrityGuard.validate_financial_entry(valid_record) is True

    # Invalid Tier 1 record without proof of work
    unverified_record = {
        "amount_usd": 500.00,
        "tier": "TIER_1_SETTLED"
    }
    with pytest.raises(EmpiricalIntegrityViolation):
        IntegrityGuard.validate_financial_entry(unverified_record)


def test_workflow_director_triage_gate():
    # Reject under minimum threshold ($25)
    res_low = WorkflowDirector.evaluate_opportunity_viability(
        title="Quick typo fix",
        payout_usd=15.00,
        channel="Reddit",
        spec_text="Fix a small typo in README.md"
    )
    assert res_low["decision"] == "REJECT_SUB_THRESHOLD"

    # Reject vague spec
    res_vague = WorkflowDirector.evaluate_opportunity_viability(
        title="Fix bug",
        payout_usd=100.00,
        channel="Discord",
        spec_text="broken code"
    )
    assert res_vague["decision"] == "REJECT_VAGUE_SPEC"

    # Qualify high-value, clear opportunity
    res_qual = WorkflowDirector.evaluate_opportunity_viability(
        title="Express CORS Reverse Proxy Server",
        payout_usd=40.00,
        channel="The Programmer's Hangout Discord",
        spec_text="Need an Express server handling incoming JSON payloads and forwarding to third party with CORS headers set."
    )
    assert res_qual["decision"] == "QUALIFIED"
    assert res_qual["qualified"] is True

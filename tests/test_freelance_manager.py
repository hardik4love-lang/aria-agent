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


def test_proposal_engine_generation():
    from aria.manager import ProposalEngine
    res = ProposalEngine.generate_proof_first_proposal(
        task_title="Next.js Hydration & LocalStorage SSR Mismatch Fix",
        problem_diagnosis="Window access during pre-render pass produces React hydration mismatch error 418.",
        solution_mechanism="Created client-only boundary with dynamic mounting state and fallback skeleton.",
        proof_gist_url="https://gist.github.com/hardik4love-lang/0494cd0e13d36aae4d0b73ac7b59fb27",
        quote_usd=50.00,
        platform="upwork"
    )
    assert res["quote_usd"] == 50.00
    assert "0494cd0e13d36aae4d0b73ac7b59fb27" in res["proposal_copy"]
    assert "Root Cause:" in res["proposal_copy"]
    assert "Fixed-Price Milestone: $50.00 USD" in res["proposal_copy"]


def test_autonomous_bounty_pipeline(tmp_path, monkeypatch):
    from aria.manager import AutonomousBountyPipeline
    
    test_opp_file = str(tmp_path / "active_opportunities.jsonl")
    monkeypatch.setattr(AutonomousBountyPipeline, "OPPORTUNITIES_FILE", test_opp_file)

    # 1. Triage and stage qualified opportunity
    staged = AutonomousBountyPipeline.evaluate_and_stage_task(
        title="Next.js LocalStorage SSR Fix",
        payout_usd=50.00,
        channel="Reactiflux Discord",
        spec_text="Fixing React hydration error when reading window.localStorage in SSR layout",
        platform="upwork"
    )
    assert staged["status"] == "STAGED"
    assert staged["payout_usd"] == 50.00
    assert "gist.github.com" in staged["gist_url"]

    # 2. Check retrieval
    opps = AutonomousBountyPipeline.get_staged_opportunities(limit=5)
    assert len(opps) == 1
    assert opps[0]["payout_usd"] == 50.00

    # 3. Check Telegram card formatting
    card = AutonomousBountyPipeline.format_opportunity_card_html(opps[0])
    assert "$50.00 USD" in card
    assert "QUALIFIED HIGH-MARGIN OPPORTUNITY DISCOVERED" in card
    assert "gist.github.com" in card

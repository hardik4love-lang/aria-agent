"""
Comprehensive Unit Tests for ARIA Superwoman Sovereign Modules:
- SOWEngine (Statement of Work & Agreements)
- DealCloser (Asymmetric Contract Negotiation)
- AriaSwarmOrchestrator (Multi-Agent Executive Task Force)
- CapitalReallocator (Anti-Fragile Market Defense & OVV)
"""

import pytest
from aria.manager.sow_engine import SOWEngine
from aria.manager.deal_closer import DealCloser
from aria.manager.capital_reallocator import CapitalReallocator
from aria.swarm.orchestrator import AriaSwarmOrchestrator


def test_sow_generation():
    sow = SOWEngine.generate_sow(
        client_name="Acme Corp",
        client_org="Enterprise SaaS",
        project_title="Stripe Webhook Verification",
        problem_statement="Signature replay attacks causing race condition.",
        deliverables=["TypeScript Next.js Route Handler", "Jest Unit Tests"],
        acceptance_tests=["Passes signature verification against valid test keys"],
        quote_usd=60.0,
        turnaround_hours=1.5
    )

    assert sow["quote_usd"] == 60.0
    assert "SOW-" in sow["sow_id"]
    assert "shruhicollections@gmail.com" in sow["markdown"]
    assert "0xFa53f5472F8bF07bd0eC88270AB81482B5A4337c" in sow["markdown"]
    assert "100% EMPIRICAL GATE" in sow["markdown"]


def test_deal_closer_price_resistance():
    res = DealCloser.resolve_objection(
        objection_type="price_resistance",
        task_title="E-Commerce Scraper",
        original_quote_usd=50.0,
        proposed_discount_usd=30.0
    )

    assert res["strategy"] == "VALUE_ANCHOR_AND_MODULAR_DECOUPLING"
    assert "$50.00" in res["response_copy"]
    assert "$30.00" in res["response_copy"]
    assert "I do not discount" in res["response_copy"]
    assert "shruhicollections@gmail.com" in res["response_copy"]


def test_deal_closer_scope_creep():
    res = DealCloser.resolve_objection(
        objection_type="scope_creep",
        task_title="Next.js Hydration Fix",
        original_quote_usd=50.0,
        creep_scope_description="Add support for dark mode and system theme synchronization"
    )

    assert res["strategy"] == "PHASED_MILESTONE_DELINEATION"
    assert "Phase 2" in res["response_copy"]
    assert "dark mode" in res["response_copy"]


def test_deal_closer_payment_friction():
    res = DealCloser.resolve_objection(
        objection_type="payment_friction",
        task_title="CORS Reverse Proxy",
        original_quote_usd=40.0,
        proof_gist_url="https://gist.github.com/hardik4love-lang/836e18aacdafa3ea310a06327db3ee3d"
    )

    assert res["strategy"] == "CRYPTOGRAPHIC_PROOF_AND_ESCROW_ENFORCEMENT"
    assert "cleanroom" in res["response_copy"]
    assert "gist.github.com" in res["response_copy"]


def test_capital_reallocator_ovv():
    # Job with high payout, fast turnaround: high OVV
    ovv_fast = CapitalReallocator.calculate_ovv(
        payout_usd=100.0,
        latency_hours=1.0,
        settlement_prob=0.95
    )
    # Stalled job with 24h latency: low OVV
    ovv_slow = CapitalReallocator.calculate_ovv(
        payout_usd=100.0,
        latency_hours=24.0,
        settlement_prob=0.90
    )

    assert ovv_fast > ovv_slow
    assert ovv_fast > 80.0


def test_capital_reallocator_pipeline_latency_audit():
    audit = CapitalReallocator.audit_pipeline_latency()
    assert audit["status"] == "ANTI_FRAGILE_OPTIMAL"
    assert any("PASSIVE_MONITORING_NO_PING" in r["status"] for r in audit["reallocations"])
    assert any("ACTIVE_CAPITAL_DEPLOYMENT" in r["status"] for r in audit["reallocations"])


def test_capital_reallocator_timeout():
    # Under hold window: maintain
    res_under = CapitalReallocator.evaluate_client_timeout("opp-123", elapsed_hours=5.0)
    assert res_under["action"] == "MAINTAIN_RESERVATION"
    assert res_under["remaining_hours"] == 19.0

    # Over hold window: release
    res_over = CapitalReallocator.evaluate_client_timeout("opp-123", elapsed_hours=26.0)
    assert res_over["action"] == "RELEASE_RESERVATION"
    assert "exceeded" in res_over["reason"]


def test_swarm_orchestrator_code_delivery():
    report = AriaSwarmOrchestrator.execute_sovereign_mission(
        mission_title="Rapid Delivery of Next.js Fix",
        mission_type="code_delivery",
        params={"job_id": "job-01"}
    )

    assert report.status == "COMPLETED"
    assert report.overall_confidence >= 0.90
    assert "CEO" in report.assigned_roles
    assert "CodeArchitect" in report.assigned_roles
    assert "SecurityAuditor" in report.assigned_roles
    assert "FinOpsGuard" in report.assigned_roles
    assert report.finops_audit["net_margin"] == "100%"
    assert report.deliverables["code_architecture"]["success"] is True


def test_swarm_orchestrator_multimedia():
    report = AriaSwarmOrchestrator.execute_sovereign_mission(
        mission_title="Produce Kailasa Short",
        mission_type="multimedia_production",
        params={"temple": "kailasa"}
    )

    assert report.status == "COMPLETED"
    assert "ContentProducer" in report.assigned_roles
    assert report.deliverables["media_production"]["format"] == "1080x1920_vertical"

"""
Tests for FinOps zero-cost compliance.
"""

from scripts.verify_zero_cost import audit_repository


def test_zero_cost_compliance():
    is_compliant, violations = audit_repository(".")
    assert is_compliant is True, f"Found FinOps cost violations: {violations}"
    assert len(violations) == 0

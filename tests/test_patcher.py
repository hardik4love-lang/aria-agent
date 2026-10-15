"""
Tests for AutonomousPatcher.
"""

from aria.github.patcher import AutonomousPatcher


def test_autonomous_patcher():
    patcher = AutonomousPatcher()
    original = "def multiply(a, b):\n    return a * b\n"
    issue = "Add type annotations and docstring"

    res = patcher.generate_patch(original, issue, "math_utils.py")
    assert res["file_path"] == "math_utils.py"
    assert res["is_valid_syntax"] is True

"""
Tests for PRReviewer and security/FinOps diff scanning.
"""

from aria.github.reviewer import PRReviewer


def test_pr_reviewer_flags_paid_endpoints():
    reviewer = PRReviewer()
    bad_diff = (
        "--- a/config.py\n"
        "+++ b/config.py\n"
        "@@ -1,3 +1,4 @@\n"
        "+OPENAI_URL = 'https://api.openai.com/v1/chat'\n"
        "+exec(user_input)\n"
    )

    violations = reviewer.scan_diff_for_violations(bad_diff)
    assert len(violations) == 2
    assert any("OpenAI" in v["message"] for v in violations)
    assert any("exec" in v["message"] for v in violations)

    review = reviewer.review_diff(pr_number=101, repo="user/aria-agent", diff_text=bad_diff)
    assert review["decision"] == "REQUEST_CHANGES"


def test_pr_reviewer_approves_safe_diff():
    reviewer = PRReviewer()
    safe_diff = (
        "--- a/utils.py\n"
        "+++ b/utils.py\n"
        "@@ -5,3 +5,4 @@\n"
        "+def add(x, y):\n"
        "+    return x + y\n"
    )

    violations = reviewer.scan_diff_for_violations(safe_diff)
    assert len(violations) == 0

    review = reviewer.review_diff(pr_number=102, repo="user/aria-agent", diff_text=safe_diff)
    assert review["decision"] == "APPROVE"

"""
Autonomous PR Review and Security/FinOps Audit Engine.
"""

import re
from typing import Dict, Any, List
from aria.llm.router import ModelRouter
from aria.security.guards import CredentialRedactor


class PRReviewer:
    """Performs automated code reviews emphasizing security, code quality, and zero-cost FinOps."""

    # Prohibited patterns that violate zero-cost bounds or zero-trust security
    FORBIDDEN_PATTERNS = [
        (r"(?i)api\.openai\.com", "Paid OpenAI endpoint violates $0.00 mandate! Use Groq or Gemini free tier."),
        (r"(?i)api\.anthropic\.com", "Paid Anthropic endpoint violates $0.00 mandate!"),
        (r"(?i)aws_access_key_id", "Potential AWS credential exposure; AWS has egress and compute fees."),
        (r"(?i)exec\(", "Dangerous dynamic `exec()` detected."),
        (r"(?i)eval\(", "Dangerous dynamic `eval()` detected."),
        (r"(?i)shell=True", "Subprocess invocation with `shell=True` poses command injection risks."),
    ]

    def __init__(self, router: ModelRouter | None = None):
        self.router = router or ModelRouter()

    def scan_diff_for_violations(self, diff_text: str) -> List[Dict[str, str]]:
        """Static rule scan across diff text."""
        violations = []
        for line_num, line in enumerate(diff_text.splitlines(), start=1):
            if line.startswith("+") and not line.startswith("+++"):
                for pattern, msg in self.FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        violations.append({
                            "line_num": str(line_num),
                            "line_content": line[:100],
                            "message": msg
                        })
        return violations

    def review_diff(self, pr_number: int, repo: str, diff_text: str) -> Dict[str, Any]:
        """Runs full static analysis and LLM architectural review on PR diff."""
        static_violations = self.scan_diff_for_violations(diff_text)
        
        # Decide approval status based on violations
        has_blockers = len(static_violations) > 0

        # LLM Synthesis Review
        client = self.router.get_client(role="planner", approx_token_count=len(diff_text) // 4)
        prompt = (
            f"Review this pull request diff for repository {repo} (PR #{pr_number}).\n"
            f"Static violations found: {len(static_violations)}\n"
            f"Diff snippet:\n{diff_text[:3000]}\n\n"
            f"Provide a concise GitHub PR Review in Markdown with:\n"
            f"1. Executive Summary\n"
            f"2. Security & FinOps Assessment (Strict $0.00 TCO check)\n"
            f"3. Recommendation: APPROVE, REQUEST_CHANGES, or COMMENT"
        )

        llm_review = client.generate(prompt=prompt, system="You are an expert DevOps and Principal Systems Architect.")

        report = {
            "pr_number": pr_number,
            "repo": repo,
            "decision": "REQUEST_CHANGES" if has_blockers else "APPROVE",
            "static_violations": static_violations,
            "review_markdown": CredentialRedactor.redact(llm_review)
        }
        return report

"""
Autonomous Email Classification and Triage Engine.
Combines instant rule-based heuristics with zero-cost LLM semantic analysis.
"""

import re
from typing import Dict, Any, Optional
from pydantic import BaseModel
from aria.llm.router import ModelRouter
from aria.security.guards import PromptInjectionGuard


class EmailClassification(BaseModel):
    category: str  # newsletter, action_required, security_alert, vip, informational, spam
    priority: str  # urgent, high, medium, low
    sentiment: str  # neutral, positive, negative, demanding
    recommended_action: str  # auto_archive, draft_reply, flag_vip, quarantine, notify_user
    confidence: float
    reason: str


class EmailClassifier:
    """Classifies emails into actionable categories without incurring unnecessary LLM costs."""

    NEWSLETTER_INDICATORS = [
        r"unsubscribe",
        r"view in browser",
        r"privacy policy",
        r"opt out",
        r"mailing list",
        r"weekly digest",
        r"newsletter",
    ]

    SECURITY_INDICATORS = [
        r"security alert",
        r"new login",
        r"password changed",
        r"unusual activity",
        r"two-factor",
        r"2fa verification",
        r"one-time password",
        r"otp code",
    ]

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()

    def classify_fast_heuristic(self, sender: str, subject: str, snippet: str) -> Optional[EmailClassification]:
        """High-speed heuristic classification (0 tokens, <1ms)."""
        combined = f"{subject} {snippet}".lower()

        # 1. Check for prompt injection attempt -> quarantine immediately
        is_safe, _, detected = PromptInjectionGuard.inspect(combined)
        if not is_safe:
            return EmailClassification(
                category="security_alert",
                priority="urgent",
                sentiment="demanding",
                recommended_action="quarantine",
                confidence=0.99,
                reason=f"Prompt injection patterns detected: {', '.join(detected)}"
            )

        # 2. Security alerts
        for pat in self.SECURITY_INDICATORS:
            if re.search(pat, combined):
                return EmailClassification(
                    category="security_alert",
                    priority="urgent",
                    sentiment="neutral",
                    recommended_action="notify_user",
                    confidence=0.95,
                    reason=f"Matches security pattern: {pat}"
                )

        # 3. Newsletters & Automated Digests
        newsletter_matches = sum(1 for pat in self.NEWSLETTER_INDICATORS if re.search(pat, combined))
        if newsletter_matches >= 2 or "noreply" in sender.lower() or "newsletter" in combined:
            return EmailClassification(
                category="newsletter",
                priority="low",
                sentiment="neutral",
                recommended_action="auto_archive",
                confidence=0.92,
                reason="Detected newsletter boilerplate / noreply sender."
            )

        return None  # Needs LLM semantic review

    def classify(self, sender: str, subject: str, snippet: str) -> EmailClassification:
        """Classifies an email, utilizing LLM only when heuristic is ambiguous."""
        heuristic = self.classify_fast_heuristic(sender, subject, snippet)
        if heuristic:
            return heuristic

        # Ambiguous: use fast executor LLM (Groq 8B)
        client = self.router.get_client(role="executor")
        prompt = (
            f"Classify this email into JSON with keys: category, priority, sentiment, recommended_action, confidence, reason.\n"
            f"Sender: {sender}\n"
            f"Subject: {subject}\n"
            f"Snippet: {snippet[:300]}\n"
            f"category must be one of: newsletter, action_required, security_alert, vip, informational, spam\n"
            f"priority must be one of: urgent, high, medium, low\n"
            f"recommended_action must be one of: auto_archive, draft_reply, flag_vip, quarantine, notify_user"
        )
        try:
            resp = client.generate(prompt=prompt, system="You are an email classification AI.")
            # Parse response
            import json
            cleaned = resp.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return EmailClassification(**data)
        except Exception:
            # Fallback default
            return EmailClassification(
                category="action_required",
                priority="medium",
                sentiment="neutral",
                recommended_action="draft_reply",
                confidence=0.80,
                reason="Default classification for action inquiry."
            )

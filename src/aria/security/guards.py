"""
Security Guardrails: Prompt Injection Defense and Sensitive Data Redaction.
"""

import re
from typing import Tuple, List


class PromptInjectionGuard:
    """Detects and isolates malicious adversarial payloads in external inputs (emails, issues, PR comments)."""

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"(?i)system\s+prompt\s*(leak|reveal|print|dump)",
        r"(?i)you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|developer|admin)",
        r"(?i)disregard\s+(all\s+)?(rules|constraints|safety)",
        r"(?i)print\s+(your\s+)?(initial|internal|system)\s+prompt",
        r"(?i)act\s+as\s+(dan|root|sudo|system)",
        r"(?i)base64\s*decode\s+and\s+execute",
        r"(?i)send\s+(all\s+)?(secrets|credentials|tokens|keys)\s+to",
        r"(?i)curl\s+https?://[^\s]+\s+-d",
    ]

    @classmethod
    def inspect(cls, content: str) -> Tuple[bool, str, List[str]]:
        """
        Inspects content for injection attempts.
        Returns: (is_safe, sanitized_content, detected_patterns)
        """
        if not content:
            return True, "", []

        detected = []
        for pattern in cls.INJECTION_PATTERNS:
            match = re.search(pattern, content)
            if match:
                detected.append(match.group(0))

        if detected:
            sanitized = f"[SECURITY QUARANTINE: Potentially adversarial content suppressed. Detected {len(detected)} patterns.]"
            return False, sanitized, detected

        return True, content, []

    @classmethod
    def wrap_external_content(cls, content: str, source_identifier: str) -> str:
        """
        Delimits external untrusted content inside isolated XML tags to defend
        against system context escape.
        """
        is_safe, processed_content, detected = cls.inspect(content)
        if not is_safe:
            return f"<untrusted_external_content source='{source_identifier}' status='FLAGGED_INJECTION'>\n{processed_content}\n</untrusted_external_content>"

        # Neutralize any raw XML closing tags in the content
        escaped = processed_content.replace("</untrusted_external_content>", "&lt;/untrusted_external_content&gt;")
        return f"<untrusted_external_content source='{source_identifier}'>\n{escaped}\n</untrusted_external_content>"


class CredentialRedactor:
    """Masks secret tokens and sensitive patterns before logging or persistence."""

    REDACTION_RULES = [
        (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[REDACTED_GH_TOKEN]"),
        (re.compile(r"github_pat_[a-zA-Z0-9_]{82}"), "[REDACTED_GH_PAT]"),
        (re.compile(r"gsk_[a-zA-Z0-9]{40,}"), "[REDACTED_GROQ_KEY]"),
        (re.compile(r"AIzaSy[a-zA-Z0-9_-]{33}"), "[REDACTED_GEMINI_KEY]"),
        (re.compile(r"(?i)password\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?"), "password=[REDACTED_PASSWORD]"),
        (re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{15,}"), "Bearer [REDACTED_BEARER]"),
    ]

    @classmethod
    def redact(cls, text: str) -> str:
        if not text:
            return ""
        result = text
        for pattern, replacement in cls.REDACTION_RULES:
            result = pattern.sub(replacement, result)
        return result

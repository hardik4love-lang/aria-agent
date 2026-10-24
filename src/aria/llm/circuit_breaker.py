"""
ARIA 3-State Resilient API Circuit Breaker.
Protects free-tier API endpoints (Groq Cloud, Google AI Studio, GitHub API)
from cascading rate limit penalties and connection timeouts.
Zero Cost of Ownership ($0.00 / month).
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("CircuitBreaker")


class CircuitBreaker:
    """3-State Circuit Breaker (CLOSED, OPEN, HALF-OPEN)."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = self.CLOSED
        self.failure_count = 0
        self.cooldown_until = 0.0

    def allow_request(self) -> bool:
        """Determines if requests should be allowed through to the target service."""
        now = time.time()
        if self.state == self.CLOSED:
            return True

        if self.state == self.OPEN:
            if now >= self.cooldown_until:
                self.state = self.HALF_OPEN
                logger.info("[CIRCUIT-BREAKER] Cooldown expired. Testing provider with canary request (HALF-OPEN)...")
                return True
            return False

        if self.state == self.HALF_OPEN:
            return True

        return True

    def record_success(self):
        """Resets the circuit to normal healthy operation upon successful API call."""
        if self.state != self.CLOSED:
            logger.info("[CIRCUIT-BREAKER] Service recovered. Resetting circuit to CLOSED.")
        self.state = self.CLOSED
        self.failure_count = 0
        self.cooldown_until = 0.0

    def record_failure(self):
        """Records an API failure (HTTP 429 rate limit or 5xx outage)."""
        self.failure_count += 1
        if self.state == self.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            self.cooldown_until = time.time() + self.cooldown_seconds
            logger.warning(
                f"[CIRCUIT-BREAKER] Threshold reached ({self.failure_count} failures). "
                f"Tripping circuit to OPEN for {self.cooldown_seconds}s."
            )

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "cooldown_remaining": max(0.0, self.cooldown_until - time.time())
        }

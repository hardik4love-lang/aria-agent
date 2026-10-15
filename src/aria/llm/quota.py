"""
Quota Tracker for Strict Zero-Cost Governance.
Tracks real-time consumption of free-tier APIs and prevents over-budget calls.
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
import httpx


class QuotaTracker:
    """Manages API rate limits and daily/hourly budgets."""

    def __init__(self, state_file_path: str = "state/quota_tracker.json"):
        self.state_file_path = state_file_path
        self.upstash_url = os.environ.get("UPSTASH_REDIS_REST_URL")
        self.upstash_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
        
        # Hard limits based on permanent free-tier quotas
        self.LIMITS = {
            "groq_daily": int(os.environ.get("GROQ_DAILY_LIMIT", 14400)),
            "gemini_daily": int(os.environ.get("GEMINI_DAILY_LIMIT", 1500)),
            "github_hourly": int(os.environ.get("GITHUB_HOURLY_LIMIT", 5000)),
        }
        
        # Safety buffers before failover (reserve buffer)
        self.BUFFERS = {
            "groq_reserve": 2000,
            "gemini_reserve": 200,
            "github_reserve": 500,
        }

    def _get_today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _get_current_hour_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")

    def _load_local_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "date": self._get_today_key(),
            "hour": self._get_current_hour_key(),
            "groq_calls": 0,
            "gemini_calls": 0,
            "github_calls": 0,
            "last_updated": time.time(),
        }

    def _save_local_state(self, state: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.state_file_path) or ".", exist_ok=True)
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def record_call(self, provider: str, count: int = 1) -> Dict[str, Any]:
        """Record an API invocation and return updated quota snapshot."""
        today = self._get_today_key()
        hour = self._get_current_hour_key()
        state = self._load_local_state()

        # Reset daily counters if day rolled over
        if state.get("date") != today:
            state["date"] = today
            state["groq_calls"] = 0
            state["gemini_calls"] = 0

        # Reset hourly counter if hour rolled over
        if state.get("hour") != hour:
            state["hour"] = hour
            state["github_calls"] = 0

        if provider == "groq":
            state["groq_calls"] = state.get("groq_calls", 0) + count
        elif provider == "gemini":
            state["gemini_calls"] = state.get("gemini_calls", 0) + count
        elif provider == "github":
            state["github_calls"] = state.get("github_calls", 0) + count

        state["last_updated"] = time.time()
        self._save_local_state(state)

        # Optional Upstash Redis sync if credentials present
        if self.upstash_url and self.upstash_token:
            try:
                # Fire and forget Redis increment via REST
                with httpx.Client(timeout=1.0) as client:
                    client.post(
                        f"{self.upstash_url}/incr/quota:{provider}:{today}",
                        headers={"Authorization": f"Bearer {self.upstash_token}"}
                    )
            except Exception:
                pass  # Local state remains authoritative on network glitch

        return self.get_snapshot()

    def get_snapshot(self) -> Dict[str, Any]:
        """Get current remaining quotas and recommendation."""
        state = self._load_local_state()
        today = self._get_today_key()
        hour = self._get_current_hour_key()

        groq_used = state.get("groq_calls", 0) if state.get("date") == today else 0
        gemini_used = state.get("gemini_calls", 0) if state.get("date") == today else 0
        github_used = state.get("github_calls", 0) if state.get("hour") == hour else 0

        groq_remaining = max(0, self.LIMITS["groq_daily"] - groq_used)
        gemini_remaining = max(0, self.LIMITS["gemini_daily"] - gemini_used)
        github_remaining = max(0, self.LIMITS["github_hourly"] - github_used)

        # Select recommended active provider
        if groq_remaining > self.BUFFERS["groq_reserve"]:
            active = "groq"
        elif gemini_remaining > self.BUFFERS["gemini_reserve"]:
            active = "gemini"
        else:
            active = "ollama"

        return {
            "groq_requests_today": groq_used,
            "groq_remaining": groq_remaining,
            "gemini_requests_today": gemini_used,
            "gemini_remaining": gemini_remaining,
            "github_requests_this_hour": github_used,
            "github_remaining": github_remaining,
            "active_provider": active,
            "within_safe_limits": (
                groq_remaining > 500 or gemini_remaining > 100 or active == "ollama"
            )
        }

    def check_availability(self, provider: str) -> Tuple[bool, str]:
        """Check if the given provider has available quota."""
        snapshot = self.get_snapshot()
        if provider == "groq":
            if snapshot["groq_remaining"] <= self.BUFFERS["groq_reserve"]:
                return False, f"Groq quota low: {snapshot['groq_remaining']} remaining."
            return True, "OK"
        elif provider == "gemini":
            if snapshot["gemini_remaining"] <= self.BUFFERS["gemini_reserve"]:
                return False, f"Gemini quota low: {snapshot['gemini_remaining']} remaining."
            return True, "OK"
        elif provider == "ollama":
            return True, "Local inference on OCI - unlimited quota."
        return True, "OK"

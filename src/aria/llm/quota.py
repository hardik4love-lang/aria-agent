"""
Quota Tracker for Strict Zero-Cost Governance.
Tracks real-time consumption of free-tier APIs and prevents over-budget calls.
Optimized with an In-Memory Write-Behind Cache for sub-millisecond lookups.
"""

import os
import json
import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
import httpx


class QuotaTracker:
    """Manages API rate limits and daily/hourly budgets with in-memory caching."""

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

        self._lock = threading.Lock()
        self._last_flush_time = time.time()
        self._dirty = False
        self._mem_cache: Optional[Dict[str, Any]] = None

    def _get_today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _get_current_hour_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")

    def _load_local_state(self) -> Dict[str, Any]:
        """Loads state from memory cache or falls back to disk."""
        with self._lock:
            if self._mem_cache is not None:
                return dict(self._mem_cache)

            if os.path.exists(self.state_file_path):
                try:
                    with open(self.state_file_path, "r", encoding="utf-8") as f:
                        self._mem_cache = json.load(f)
                        return dict(self._mem_cache)
                except Exception:
                    pass

            self._mem_cache = {
                "date": self._get_today_key(),
                "hour": self._get_current_hour_key(),
                "groq_calls": 0,
                "gemini_calls": 0,
                "github_calls": 0,
                "last_updated": time.time(),
            }
            return dict(self._mem_cache)

    def flush(self) -> None:
        """Flushes in-memory dirty cache to persistent disk storage."""
        with self._lock:
            if not self._dirty or self._mem_cache is None:
                return
            try:
                os.makedirs(os.path.dirname(self.state_file_path) or ".", exist_ok=True)
                with open(self.state_file_path, "w", encoding="utf-8") as f:
                    json.dump(self._mem_cache, f, indent=2)
                self._dirty = False
                self._last_flush_time = time.time()
            except Exception as e:
                print(f"[!] QuotaTracker flush error: {e}")

    def record_call(self, provider: str, count: int = 1) -> Dict[str, Any]:
        """Record an API invocation in memory and conditionally flush."""
        today = self._get_today_key()
        hour = self._get_current_hour_key()

        with self._lock:
            if self._mem_cache is None:
                # populate cache
                if os.path.exists(self.state_file_path):
                    try:
                        with open(self.state_file_path, "r", encoding="utf-8") as f:
                            self._mem_cache = json.load(f)
                    except Exception:
                        self._mem_cache = {}
                else:
                    self._mem_cache = {}

            # Reset daily counters if day rolled over
            if self._mem_cache.get("date") != today:
                self._mem_cache["date"] = today
                self._mem_cache["groq_calls"] = 0
                self._mem_cache["gemini_calls"] = 0

            # Reset hourly counter if hour rolled over
            if self._mem_cache.get("hour") != hour:
                self._mem_cache["hour"] = hour
                self._mem_cache["github_calls"] = 0

            if provider == "groq":
                self._mem_cache["groq_calls"] = self._mem_cache.get("groq_calls", 0) + count
            elif provider == "gemini":
                self._mem_cache["gemini_calls"] = self._mem_cache.get("gemini_calls", 0) + count
            elif provider == "github":
                self._mem_cache["github_calls"] = self._mem_cache.get("github_calls", 0) + count

            self._mem_cache["last_updated"] = time.time()
            self._dirty = True

        # Flush write-behind cache immediately to preserve consistency
        self.flush()

        # Optional Upstash Redis sync if credentials present
        if self.upstash_url and self.upstash_token:
            try:
                with httpx.Client(timeout=1.0) as client:
                    client.post(
                        f"{self.upstash_url}/incr/quota:{provider}:{today}",
                        headers={"Authorization": f"Bearer {self.upstash_token}"}
                    )
            except Exception:
                pass

        return self.get_snapshot()

    def get_snapshot(self) -> Dict[str, Any]:
        """Get current remaining quotas and recommendation with in-memory speed."""
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

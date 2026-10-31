#!/usr/bin/env python3
"""
ARIA Repo Language & Stack Fingerprinting.
Tracks per-repo success rates and provides a language_confidence_multiplier
for issue scoring. ARIA learns which stacks she wins at and self-routes.
"""
import json, pathlib, time, logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

FINGERPRINTS_FILE = pathlib.Path("data/repo_fingerprints.json")

# Default confidence multipliers per language (ARIA's known strengths)
LANGUAGE_BASE_CONFIDENCE = {
    "python": 1.3,
    "go": 1.2,
    "typescript": 1.1,
    "javascript": 1.1,
    "rust": 0.7,    # Hard — penalize until proven
    "c": 0.8,
    "c++": 0.75,
    "java": 0.9,
    "unknown": 1.0,
}

class RepoFingerprints:
    def __init__(self, fingerprints_file: pathlib.Path = FINGERPRINTS_FILE):
        self.fp_file = fingerprints_file
        self.data: Dict[str, dict] = self._load()

    def _load(self) -> dict:
        if self.fp_file.exists():
            try:
                return json.loads(self.fp_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save(self):
        self.fp_file.parent.mkdir(parents=True, exist_ok=True)
        self.fp_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def get_or_create(self, repo: str) -> dict:
        if repo not in self.data:
            self.data[repo] = {
                "repo": repo,
                "language": "unknown",
                "stack": [],
                "attempts": 0,
                "merges": 0,
                "rejections": 0,
                "success_rate": 0.0,
                "avg_merge_time_days": None,
                "last_attempt_ts": None,
                "created_ts": time.time()
            }
        return self.data[repo]

    def set_language(self, repo: str, language: str, stack: list = None):
        """Set the primary language and stack tags for a repo."""
        fp = self.get_or_create(repo)
        fp["language"] = language.lower()
        if stack:
            fp["stack"] = stack
        self._save()

    def record_attempt(self, repo: str):
        """Call when ARIA opens a PR to this repo."""
        fp = self.get_or_create(repo)
        fp["attempts"] += 1
        fp["last_attempt_ts"] = time.time()
        self._recalculate(fp)
        self._save()

    def record_merge(self, repo: str, merge_time_days: float = None):
        """Call when a PR from this repo gets merged."""
        fp = self.get_or_create(repo)
        fp["merges"] += 1
        if merge_time_days is not None:
            if fp["avg_merge_time_days"] is None:
                fp["avg_merge_time_days"] = merge_time_days
            else:
                # Exponential moving average
                fp["avg_merge_time_days"] = 0.7 * fp["avg_merge_time_days"] + 0.3 * merge_time_days
        self._recalculate(fp)
        self._save()
        logger.info(f"[Fingerprint] MERGE recorded for {repo} | success_rate={fp['success_rate']:.2f}")

    def record_rejection(self, repo: str):
        """Call when a PR from this repo is closed without merge."""
        fp = self.get_or_create(repo)
        fp["rejections"] += 1
        self._recalculate(fp)
        self._save()
        logger.info(f"[Fingerprint] REJECTION recorded for {repo} | success_rate={fp['success_rate']:.2f}")

    def _recalculate(self, fp: dict):
        total = fp["merges"] + fp["rejections"]
        if total > 0:
            fp["success_rate"] = fp["merges"] / total
        else:
            fp["success_rate"] = 0.0

    def get_confidence_multiplier(self, repo: str, language_hint: str = None) -> float:
        """
        Returns a score multiplier (0.5 to 2.0) for issue scoring.
        Combines: language base confidence + learned success rate.
        Called by bounty_hourly_daemon.py during issue scoring.
        """
        fp = self.data.get(repo, {})
        lang = fp.get("language", language_hint or "unknown").lower()
        base = LANGUAGE_BASE_CONFIDENCE.get(lang, 1.0)

        attempts = fp.get("attempts", 0)
        success_rate = fp.get("success_rate", 0.0)

        if attempts < 3:
            # Not enough data — use language base only
            multiplier = base
        else:
            # Blend: 50% language base + 50% learned success rate (scaled 0→2)
            learned = success_rate * 2.0  # 100% success = 2.0x
            multiplier = 0.5 * base + 0.5 * learned

        # Clamp to sane range
        multiplier = max(0.5, min(2.0, multiplier))
        logger.debug(f"[Fingerprint] {repo} confidence={multiplier:.2f} (lang={lang}, attempts={attempts}, rate={success_rate:.2f})")
        return multiplier

    def infer_language_from_repo_name(self, repo: str) -> str:
        """Cheap heuristic from repo name/known repos."""
        name = repo.lower()
        if any(x in name for x in ["go-", "golang", "hy-", "hybrid"]):
            return "go"
        if any(x in name for x in ["py", "python", "django", "flask"]):
            return "python"
        if any(x in name for x in ["ts", "next", "react", "node", "cal", "omi"]):
            return "typescript"
        if any(x in name for x in ["rust", "cargo", "tt-metal"]):
            return "rust"
        return "unknown"

    def summary(self) -> dict:
        return {
            "total_repos_tracked": len(self.data),
            "repos": [
                {
                    "repo": v["repo"],
                    "language": v["language"],
                    "success_rate": round(v["success_rate"], 2),
                    "attempts": v["attempts"],
                    "merges": v["merges"]
                }
                for v in self.data.values()
            ]
        }

"""
Email Behavioral Pattern Learner.
Learns preferences from human operator feedback to automate future decisions.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional


class PatternLearner:
    """Stores and retrieves learned email handling rules."""

    def __init__(self, pattern_file: str = "state/email_patterns.json"):
        self.pattern_file = pattern_file
        os.makedirs(os.path.dirname(self.pattern_file) or ".", exist_ok=True)

    def _load_patterns(self) -> Dict[str, Any]:
        if os.path.exists(self.pattern_file):
            try:
                with open(self.pattern_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "vip_senders": [],
            "auto_archive_domains": [],
            "custom_rules": []
        }

    def _save_patterns(self, data: Dict[str, Any]) -> None:
        with open(self.pattern_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_vip_sender(self, email_address: str) -> None:
        patterns = self._load_patterns()
        clean = email_address.strip().lower()
        if clean not in patterns["vip_senders"]:
            patterns["vip_senders"].append(clean)
            self._save_patterns(patterns)

    def is_vip(self, email_address: str) -> bool:
        patterns = self._load_patterns()
        return email_address.strip().lower() in patterns.get("vip_senders", [])

    def record_operator_decision(self, sender: str, subject: str, action: str) -> None:
        """Records an operator approval or modification to refine future classifications."""
        patterns = self._load_patterns()
        rule = {
            "sender": sender.lower(),
            "subject_keyword": subject.lower().split()[0] if subject else "",
            "action": action,
            "recorded_at": time.time()
        }
        patterns["custom_rules"].append(rule)
        # Keep last 100 rules
        patterns["custom_rules"] = patterns["custom_rules"][-100:]
        self._save_patterns(patterns)

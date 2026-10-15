"""
Git-Native State Store.
Implements the Git-as-Transaction-Log pattern for zero-cost permanent persistence.
"""

import os
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any


class GitStateStore:
    """Manages append-only JSONL state logs and commits to the state branch/repository."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.state_dir = os.path.join(root_dir, "state")
        self.logs_dir = os.path.join(self.state_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

    def append_audit_log(self, task_id: str, event_type: str, details: Dict[str, Any]) -> str:
        """Appends an event to the monthly audit JSONL log."""
        os.makedirs(self.logs_dir, exist_ok=True)
        month_str = datetime.now(timezone.utc).strftime("%Y-%m")
        log_file = os.path.join(self.logs_dir, f"audit_{month_str}.jsonl")
        
        import json
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "event_type": event_type,
            "details": details
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return log_file

    def commit_transaction(self, message: str) -> bool:
        """Stages state changes and commits using the configured Git bot identity."""
        try:
            # Check if inside a git repository
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.root_dir, check=True, capture_output=True)
            
            subprocess.run(["git", "config", "user.name", "ARIA Agent Bot"], cwd=self.root_dir, check=True)
            subprocess.run(["git", "config", "user.email", "aria-agent@users.noreply.github.com"], cwd=self.root_dir, check=True)
            
            subprocess.run(["git", "add", "state/"], cwd=self.root_dir, check=True)
            
            # Check if there are changes to commit
            status = subprocess.run(["git", "status", "--porcelain", "state/"], cwd=self.root_dir, capture_output=True, text=True)
            if not status.stdout.strip():
                return False  # No state changes

            subprocess.run(["git", "commit", "-m", f"chore(state): {message}"], cwd=self.root_dir, check=True)
            return True
        except Exception:
            return False

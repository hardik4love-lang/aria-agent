"""
Human Approval Governance.
Enforces out-of-band validation for high-risk actions (email sending, repo mutations).
"""

import os
from typing import Dict, Any, Tuple
import httpx


class HumanApprovalGate:
    """Manages push-based approvals via Ntfy.sh (permanent zero-cost push notification service)."""

    HIGH_RISK_TOOLS = {
        "email_send",
        "gh_commit_file",
        "gh_create_pr",
        "gh_merge_pr",
        "code_execute_sandbox",
    }

    def __init__(self):
        self.topic = os.environ.get("NTFY_TOPIC", "aria-default-notifications")
        self.auto_approval = os.environ.get("AUTO_APPROVAL_ENABLED", "false").lower() == "true"
        self.whitelist = [
            x.strip().lower() 
            for x in os.environ.get("AUTO_APPROVAL_WHITELIST", "").split(",") 
            if x.strip()
        ]

    def is_action_high_risk(self, tool_name: str, tool_args: Dict[str, Any]) -> bool:
        """Determines if the action requires explicit human verification."""
        if tool_name not in self.HIGH_RISK_TOOLS:
            return False

        # Specific exemptions: sending email to user's own whitelisted address
        if tool_name == "email_send":
            recipient = str(tool_args.get("recipient", "")).lower()
            if recipient in self.whitelist:
                return False

        if self.auto_approval:
            return False

        return True

    def request_approval(self, task_id: str, action_desc: str, tool_name: str, tool_args: Dict[str, Any]) -> Tuple[bool, str]:
        """Sends an out-of-band notification to the operator's mobile device via Ntfy."""
        message = (
            f"ARIA AGENT APPROVAL REQUIRED\n"
            f"Task: {task_id}\n"
            f"Action: {tool_name}\n"
            f"Summary: {action_desc}\n"
            f"Args: {tool_args}"
        )

        headers = {
            "Title": f"ARIA Security Alert: {tool_name}",
            "Priority": "high",
            "Tags": "warning,robot",
            "Actions": "view, Review State, https://github.com"
        }

        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(
                    f"https://ntfy.sh/{self.topic}",
                    data=message.encode("utf-8"),
                    headers=headers
                )
                if resp.status_code == 200:
                    return True, f"Notification dispatched to ntfy.sh/{self.topic}"
                return False, f"Ntfy status code {resp.status_code}"
        except Exception as e:
            return False, f"Failed to deliver notification: {str(e)}"

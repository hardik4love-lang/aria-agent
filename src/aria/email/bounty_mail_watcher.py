"""
ARIA 1-Minute Bounty & Client Email Watcher with Intelligent Noise Filtering.
Monitors incoming inbox messages every 60 seconds for verified PR reviews,
bounty settlements (PayPal, USDC), maintainer decisions, and genuine client hiring.
Filters out bot spam, competitor bids, and community chatter.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional

from aria.tools.email_tools import EmailTools
from aria.security.telegram_gate import TelegramApprovalGate

logger = logging.getLogger("BountyMailWatcher")


class BountyMailWatcher:
    """Watches inbox every 60 seconds and notifies operator of high-priority, actionable updates."""

    # Keywords that indicate genuine maintainer action or monetary settlement
    HIGH_PRIORITY_KEYWORDS = [
        "approved your pull request", "changes requested", "review submitted",
        "bounty awarded", "payment received", "paypal transfer", "sent you money",
        "invoice paid", "hired you", "merge conflict detected", "preflight verdict",
        "payout sent", "bounty settled"
    ]

    # Noisy bot chatter to drop immediately
    IGNORE_KEYWORDS = [
        "/opire try", "/attempt", "/try", "fuma2514", "i can deliver this",
        "run failed: autoland", "run failed: aria automated maintenance",
        "run failed: ci/autoland"
    ]

    def __init__(self):
        self.email_tools = EmailTools()
        self.telegram = TelegramApprovalGate()
        self.seen_uids = set()

    def check_inbox_cycle(self) -> List[Dict[str, Any]]:
        """Checks for new unread emails and alerts operator if actionable."""
        try:
            emails = self.email_tools.email_list_unread(max_count=10)
        except Exception as e:
            logger.warning(f"Error checking inbox: {e}")
            return []

        alerts = []
        for em in emails:
            uid = em.get("uid", "")
            if uid in self.seen_uids:
                continue
            self.seen_uids.add(uid)

            subject = em.get("subject", "")
            sender = em.get("sender", "")
            snippet = em.get("snippet", "")

            combined = f"{subject} {sender} {snippet}".lower()

            # Skip noisy automated chatter
            if any(ign in combined for ign in self.IGNORE_KEYWORDS):
                continue

            # Check if actionable
            is_actionable = any(k in combined for k in self.HIGH_PRIORITY_KEYWORDS)

            if is_actionable:
                logger.info(f"[!] Actionable event detected: {subject}")
                alerts.append(em)
                self._dispatch_telegram_alert(em)

        return alerts

    def _dispatch_telegram_alert(self, em: Dict[str, Any]):
        subject = em.get("subject", "No Subject")
        sender = em.get("sender", "Unknown")
        snippet = em.get("snippet", "")[:250]
        date_str = em.get("date", time.strftime("%Y-%m-%d %H:%M:%S"))

        alert_msg = (
            f"<b>📬 ACTIONABLE BOUNTY / CLIENT EMAIL ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Subject:</b> <code>{subject}</code>\n"
            f"<b>From:</b> <i>{sender}</i>\n"
            f"<b>Date:</b> {date_str}\n\n"
            f"<b>Summary:</b>\n"
            f"<blockquote>{snippet}</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Noise filtered. Only actionable maintainer & payout events alert you.</i>"
        )
        try:
            from aria.security.telegram_bot_service import TelegramAssistantService
            svc = TelegramAssistantService()
            svc.send_message(alert_msg, reply_markup=svc.get_main_menu_keyboard())
        except Exception as e:
            logger.error(f"Could not forward email alert to Telegram: {e}")

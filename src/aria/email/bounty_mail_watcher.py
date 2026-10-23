"""
ARIA 1-Minute Bounty & Client Email Watcher.
Monitors incoming inbox messages every 60 seconds for PR updates,
bounty alerts (Go-Hybrid, Tenstorrent, Algora), and client payments.
Dispatches high-priority push notifications to Telegram.
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
    """Watches inbox every 60 seconds and notifies operator of bounty updates."""

    BOUNTY_KEYWORDS = [
        "go-hybrid", "limitlessprojects", "tenstorrent", "tt-metal",
        "algora", "bounty", "pull request", "shepherd", "preflight",
        "slavelabour", "paypal", "payment", "upi", "hiring", "invoice"
    ]

    def __init__(self):
        self.email_tools = EmailTools()
        self.telegram = TelegramApprovalGate()
        self.seen_uids = set()

    def check_inbox_cycle(self) -> List[Dict[str, Any]]:
        """Checks for new unread emails and alerts operator if bounty-related."""
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

            # Check for bounty keywords
            combined = f"{subject} {sender} {snippet}".lower()
            is_bounty_event = any(k in combined for k in self.BOUNTY_KEYWORDS)

            if is_bounty_event:
                logger.info(f"[!] Bounty/Client event detected: {subject}")
                alerts.append(em)
                self._dispatch_telegram_alert(em)

        return alerts

    def _dispatch_telegram_alert(self, em: Dict[str, Any]):
        subject = em.get("subject", "No Subject")
        sender = em.get("sender", "Unknown")
        snippet = em.get("snippet", "")[:250]
        date_str = em.get("date", time.strftime("%Y-%m-%d %H:%M:%S"))

        alert_msg = (
            f"<b>📬 NEW BOUNTY / CLIENT EMAIL ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Subject:</b> <code>{subject}</code>\n"
            f"<b>From:</b> <i>{sender}</i>\n"
            f"<b>Date:</b> {date_str}\n\n"
            f"<b>Preview:</b>\n"
            f"<blockquote>{snippet}</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>ARIA is monitoring your pipeline 24/7.</i>"
        )
        try:
            from aria.security.telegram_bot_service import TelegramAssistantService
            svc = TelegramAssistantService()
            svc.send_message(alert_msg, reply_markup=svc.get_main_menu_keyboard())
        except Exception as e:
            logger.error(f"Could not forward email alert to Telegram: {e}")

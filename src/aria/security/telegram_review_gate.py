"""
ARIA 2-Way Telegram Human-in-the-Loop Review Gate.

Replaces automated unreviewed PR spam with a clean operator control card:
1. Shows target issue, verified bounty amount, and issue URL.
2. Displays test pass proof (e.g. 18 passed in 4.2s).
3. Provides collapsible unified git diff.
4. Provides 1-tap mobile decision buttons:
   - [🚀 Approve & Open PR]
   - [🔄 Re-try Patch]
   - [❌ Discard]
"""

import os
import json
import logging
import urllib.request
from typing import Dict, Any, Optional

logger = logging.getLogger("TelegramReviewGate")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8737013099")


class TelegramReviewGate:
    """Delivers verified patch review cards to operator Telegram for one-click approval."""

    @staticmethod
    def send_patch_for_approval(
        task_id: str,
        repo: str,
        issue_number: int,
        issue_title: str,
        issue_url: str,
        bounty_usd: float,
        diff_summary: str,
        diff_text: str,
        test_summary: str
    ) -> bool:
        """Sends an interactive Telegram card for the operator to approve opening the PR."""
        # Truncate diff to fit Telegram message limits
        diff_snippet = diff_text[:700] if len(diff_text) > 700 else diff_text

        msg = (
            f"🎯 <b>VERIFIED BOUNTY PATCH READY FOR REVIEW</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📁 <b>Repo:</b> <code>{repo}</code>\n"
            f"💰 <b>Bounty:</b> <b>${bounty_usd:,.2f} USD</b>\n"
            f"📌 <b>Issue:</b> <a href=\"{issue_url}\">#{issue_number}: {issue_title}</a>\n\n"
            f"🧪 <b>Hermetic Tests:</b> <i>{test_summary}</i>\n"
            f"📊 <b>Diff:</b> <code>{diff_summary}</code>\n\n"
            f"<b>Patch Preview:</b>\n"
            f"<pre><code>{diff_snippet}</code></pre>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Verified passing tests. Tap to authorize upstream Pull Request.</i>"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🚀 Approve & Open PR", "callback_data": f"PR_APPROVE:{task_id}"},
                    {"text": "🔄 Retry Fix", "callback_data": f"PR_RETRY:{task_id}"}
                ],
                [
                    {"text": "❌ Discard", "callback_data": f"PR_DISCARD:{task_id}"}
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": keyboard
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to deliver patch review card to Telegram: {e}")
            return False

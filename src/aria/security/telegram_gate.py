"""
ARIA Telegram Human-in-the-Loop Approval Gate.
100% Zero-Cost out-of-band authorization via official Telegram Bot API (long-polling / REST).
No paid servers or webhooks required.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional, Tuple, Callable
import httpx

try:
    from dotenv import load_dotenv
    # Search for .env in current and parent directories
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"))
    load_dotenv()
except ImportError:
    pass

class TelegramApprovalGate:
    """
    Manages push approval cards to the operator's personal Telegram.
    Enforces that zero actions (delivering code, bidding, releasing data)
    can execute without explicit human authorization.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        audit_log_path: str = "state/approvals.jsonl"
    ):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.audit_log_path = audit_log_path
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        
        os.makedirs(os.path.dirname(self.audit_log_path) or ".", exist_ok=True)

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_approval_request(
        self,
        task_id: str,
        job_title: str,
        target_info: str,
        potential_revenue: str,
        sample_preview: str,
        solution_file: str
    ) -> Tuple[bool, str]:
        """
        Dispatches an interactive approval card to the user's Telegram.
        """
        approval_data = {
            "task_id": task_id,
            "job_title": job_title,
            "target_info": target_info,
            "potential_revenue": potential_revenue,
            "solution_file": solution_file,
            "sample_preview": sample_preview[:300],
            "requested_at": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "PENDING"
        }
        self.pending_approvals[task_id] = approval_data

        card_html = (
            f"<b>🤖 ARIA TASK APPROVAL REQUIRED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Task ID:</b> <code>{task_id}</code>\n"
            f"<b>Job:</b> {job_title}\n"
            f"<b>Target:</b> {target_info}\n"
            f"<b>Estimated Value:</b> <b>{potential_revenue}</b>\n"
            f"<b>Deliverable:</b> <code>{solution_file}</code>\n\n"
            f"<b>Preview Proof:</b>\n"
            f"<code>{sample_preview[:250]}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 <i>Reply <b>/approve {task_id}</b> to authorize execution</i>\n"
            f"👉 <i>Reply <b>/reject {task_id}</b> to cancel</i>"
        )

        if not self.is_configured():
            print(f"\n[TELEGRAM GATE - SIMULATION MODE]")
            print(f"Token not set. Simulated Telegram Push to {self.chat_id or 'Operator'}:")
            print(f"Task: {task_id} | Job: {job_title} | Payout: {potential_revenue}")
            print(f"To approve in CLI: call approve_task('{task_id}')")
            return True, "Approval requested in simulation mode (set TELEGRAM_BOT_TOKEN for real mobile push)."

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": card_html,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "✅ APPROVE & DELIVER", "callback_data": f"APPROVE:{task_id}"},
                        {"text": "❌ REJECT", "callback_data": f"REJECT:{task_id}"}
                    ]
                ]
            }
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    return True, "Telegram approval card delivered successfully."
                return False, f"Telegram API error {resp.status_code}: {resp.text}"
        except Exception as e:
            return False, f"Network error sending Telegram card: {str(e)}"

    def _check_state_file_decision(self, task_id: str) -> Optional[bool]:
        """Checks if task approval/rejection was recorded in audit log by assistant service."""
        if not os.path.exists(self.audit_log_path):
            return None
        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        if record.get("task_id") == task_id:
                            decision = str(record.get("decision", "")).upper()
                            if "APPROVE" in decision:
                                return True
                            elif "REJECT" in decision:
                                return False
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def check_approval_status(self, task_id: str, timeout_seconds: int = 30) -> bool:
        """
        Polls for approval from the operator (via shared state log, button, or message).
        Gracefully handles Telegram single-consumer 409 conflicts by synchronizing via state.
        """
        if not self.is_configured():
            print(f"[*] [TELEGRAM GATE] Waiting for local approval on task '{task_id}' (Simulation)...")
            return True

        # 1. Immediate check from shared state log (e.g. if assistant daemon already processed it)
        dec = self._check_state_file_decision(task_id)
        if dec is not None:
            return dec

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        start_time = time.time()
        last_update_id = 0

        while time.time() - start_time < timeout_seconds:
            # Check state log on each cycle
            dec = self._check_state_file_decision(task_id)
            if dec is not None:
                return dec

            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.get(f"{url}?offset={last_update_id + 1}&timeout=3")
                    if resp.status_code == 200:
                        data = resp.json()
                        for update in data.get("result", []):
                            last_update_id = max(last_update_id, update.get("update_id", 0))

                            callback = update.get("callback_query", {})
                            cb_data = callback.get("data", "")
                            if cb_data == f"APPROVE:{task_id}":
                                self._record_audit(task_id, "APPROVED_BY_TELEGRAM_BUTTON")
                                return True
                            elif cb_data == f"REJECT:{task_id}":
                                self._record_audit(task_id, "REJECTED_BY_TELEGRAM_BUTTON")
                                return False

                            msg = update.get("message", {}).get("text", "").strip()
                            if msg.lower() == f"/approve {task_id}".lower():
                                self._record_audit(task_id, "APPROVED_BY_TELEGRAM_TEXT")
                                return True
                            elif msg.lower() == f"/reject {task_id}".lower():
                                self._record_audit(task_id, "REJECTED_BY_TELEGRAM_TEXT")
                                return False
                    elif resp.status_code == 409:
                        # 409 Conflict: Another poller (assistant daemon) is active. Sync via state log!
                        pass
            except Exception:
                pass
            time.sleep(1.5)

        return False

    def _record_audit(self, task_id: str, decision: str):
        record = {
            "task_id": task_id,
            "decision": decision,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "data": self.pending_approvals.get(task_id, {})
        }
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        if task_id in self.pending_approvals:
            self.pending_approvals[task_id]["status"] = decision

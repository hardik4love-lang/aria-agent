#!/usr/bin/env python3
import os
import httpx
from typing import Dict, Any, Optional

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def relay_alert(title: str, message: str, color_hex: int = 0x38BDF8) -> Dict[str, bool]:
    results = {"discord": False, "telegram": False}
    with httpx.Client(timeout=8.0) as client:
        if DISCORD_WEBHOOK:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": color_hex
                }]
            }
            try:
                r = client.post(DISCORD_WEBHOOK, json=payload)
                results["discord"] = r.status_code in [200, 204]
            except Exception:
                pass

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"<b>{title}</b>\n\n{message}",
                "parse_mode": "HTML"
            }
            try:
                r = client.post(tg_url, json=payload)
                results["telegram"] = r.status_code == 200
            except Exception:
                pass
    return results

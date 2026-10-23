#!/usr/bin/env python3
"""
Connects Aria to the Operator's Telegram account via @Ariabountie_bot.
Polls for /start or any message from the operator, captures the chat_id,
writes to .env, and sends an immediate welcome test message.
"""

import os
import sys
import time
import httpx

BOT_TOKEN = "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA"
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

def connect_operator(timeout_seconds: int = 120):
    print("==================================================================")
    print("  ARIA TELEGRAM GATEWAY PAIRING")
    print(f"  Bot: @Ariabountie_bot")
    print("==================================================================")
    print("\n[!] ACTION REQUIRED: Open Telegram, search for @Ariabountie_bot")
    print("    Link: https://t.me/Ariabountie_bot")
    print("    Click 'START' or send any message (e.g. /start)\n")
    print(f"[*] Listening for incoming message (Timeout: {timeout_seconds}s)...")

    start_time = time.time()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    while time.time() - start_time < timeout_seconds:
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    updates = resp.json().get("result", [])
                    if updates:
                        last_update = updates[-1]
                        msg = last_update.get("message", {}) or last_update.get("callback_query", {}).get("message", {})
                        chat = msg.get("chat", {})
                        chat_id = str(chat.get("id", ""))
                        first_name = chat.get("first_name", "Operator")
                        username = chat.get("username", "Unknown")

                        if chat_id:
                            print(f"\n[+] MESSAGE RECEIVED!")
                            print(f"[+] Operator: {first_name} (@{username})")
                            print(f"[+] Chat ID: {chat_id}")

                            # Write to .env
                            update_env_file(chat_id)

                            # Send Welcome Card to Operator
                            send_welcome_card(chat_id, first_name)
                            return True
        except Exception as e:
            print(f"[!] Polling error: {e}")

        time.sleep(2)
        print(".", end="", flush=True)

    print("\n[-] Timeout reached without receiving /start from operator.")
    return False

def update_env_file(chat_id: str):
    env_lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            env_lines = f.readlines()

    keys_to_set = {
        "TELEGRAM_BOT_TOKEN": BOT_TOKEN,
        "TELEGRAM_CHAT_ID": chat_id,
        "PAYPAL_EMAIL": "shruhicollections@gmail.com",
        "UPI_ID": "purshottamramawat27@oksbi"
    }

    new_lines = []
    existing_keys = set()
    for line in env_lines:
        key = line.split("=")[0].strip() if "=" in line else ""
        if key in keys_to_set:
            new_lines.append(f"{key}={keys_to_set[key]}\n")
            existing_keys.add(key)
        else:
            new_lines.append(line)

    for k, v in keys_to_set.items():
        if k not in existing_keys:
            new_lines.append(f"{k}={v}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"[OK] Saved credentials to {ENV_PATH}")

def send_welcome_card(chat_id: str, first_name: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = (
        f"<b>🎉 ARIA CONNECTED SUCCESSFULLY!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Operator:</b> {first_name} (Authenticated)\n"
        f"<b>TCO Governance:</b> $0.00 / month (100% Sovereign)\n"
        f"<b>Payout Channels:</b>\n"
        f"  • PayPal: <code>shruhicollections@gmail.com</code>\n"
        f"  • UPI: <code>purshottamramawat27@oksbi</code>\n\n"
        f"<b>Hourly Scraper Status:</b> 10 targets/hr armed\n"
        f"<b>Telegram Approval Gate:</b> ACTIVE & ENFORCED\n\n"
        f"<i>Every hour, Aria will extract 10 targets and send an approval card here. Zero actions will be dispatched without your approval!</i>"
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    with httpx.Client(timeout=8.0) as client:
        res = client.post(url, json=payload)
        if res.status_code == 200:
            print("[OK] Welcome card dispatched to operator's Telegram.")
        else:
            print(f"[-] Failed to send welcome card: {res.text}")

if __name__ == "__main__":
    connect_operator()

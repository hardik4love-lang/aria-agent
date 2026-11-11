"""
Aria Human-in-the-Loop Rapid Payout Radar & Solver Dispatcher.
1. Scrapes active remote jobs ($50 - $200) across verified global platforms (NO Freelancer, NO Reddit).
2. Runs Triple-Agent Payment Verification Council (100% unanimous 3/3 consensus required).
3. Dispatches verified opportunities directly to Telegram for user one-tap review and approval.
4. Holds execution until user signals approval to solve and submit PR.
"""

import os
import sys
import json
import httpx
from datetime import datetime
from aria.verification.triple_agent_verifier import TripleAgentPaymentVerifier

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA"
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or "8737013099"
SEEN_JOBS_FILE = "D:/aria-agent/data/seen_dispatched_jobs.json"
OUTPUT_FILE = "D:/aria-agent/data/verified_rapid_payout_jobs.json"

def send_telegram_alert(job):
    msg = (
        f"⚡ *Aria Verified Task Alert (3/3 Consensus)*\n\n"
        f"📌 *Title:* {job.get('title')}\n"
        f"💰 *Payout:* ${job.get('budget_usd'):.2f} USD\n"
        f"🏢 *Platform / Rail:* {job.get('platform').upper()}\n"
        f"⏱️ *Turnaround:* {job.get('payout_turnaround_hours', 24)}h\n"
        f"🛡️ *Council Verdict:*\n"
        f"  • Escrow: {job['agent_1_escrow']['verdict']}\n"
        f"  • Trust: {job['agent_2_counterparty']['verdict']}\n"
        f"  • Scope: {job['agent_3_rapid_scope']['verdict']}\n\n"
        f"🔗 [Direct Task Link]({job.get('url')})\n\n"
        f"👉 *Action:* Reply 'SOLVE {job.get('job_id')}' to authorize automated PR creation."
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = httpx.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=10.0)
        return r.status_code == 200 and r.json().get("ok")
    except Exception as e:
        print(f"[!] Telegram send error: {e}")
        return False

def run_radar():
    print("[*] Running Aria Human-in-the-Loop Radar...")
    from scripts.scan_and_verify_rapid_jobs import run_pipeline
    verified_jobs = run_pipeline()
    
    # Load seen jobs
    os.makedirs(os.path.dirname(SEEN_JOBS_FILE), exist_ok=True)
    seen_ids = set()
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                seen_ids = set(json.load(f))
        except:
            seen_ids = set()

    dispatched = 0
    for j in verified_jobs:
        jid = str(j.get("job_id"))
        if jid not in seen_ids:
            if send_telegram_alert(j):
                seen_ids.add(jid)
                dispatched += 1
                print(f"[+] Dispatched alert to Telegram: {j.get('title')}")
                if dispatched >= 3: # throttle per run
                    break

    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f, indent=2)

    print(f"[OK] Radar cycle complete. Dispatched {dispatched} new verified tasks to Telegram.")

if __name__ == "__main__":
    run_radar()

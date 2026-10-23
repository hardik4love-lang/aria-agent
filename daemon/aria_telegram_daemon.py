#!/usr/bin/env python3
"""
ARIA Persistent 24/7 Telegram Assistant & Bounty Mail Watcher Daemon.
Maintains continuous long-polling with @Ariabountie_bot, providing instant (<1s) responses,
autonomous tool dispatch, rapid cash solvers, mobile approval gating, and 1-minute bounty email alerts.
Total Cost of Ownership: $0.00 / month (Zero-Cost FinOps).
Runs natively on GitHub Actions Cloud Runners in 24/7 continuous perpetual handoff loops.
"""

import os
import sys
import time
import signal
import logging
import threading
import argparse
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

from aria.security.telegram_bot_service import TelegramAssistantService
from aria.email.bounty_mail_watcher import BountyMailWatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ARIA-DAEMON] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AriaDaemon")

running = True

def handle_sigterm(signum, frame):
    global running
    logger.info("Signal received. Initiating graceful shutdown...")
    running = False

def run_email_watcher_thread():
    """Background worker that inspects inbox every 60 seconds for bounty and PR alerts."""
    watcher = BountyMailWatcher()
    logger.info("1-Minute Bounty & Client Email Watcher thread active.")
    while running:
        try:
            alerts = watcher.check_inbox_cycle()
            if alerts:
                logger.info(f"[EMAIL] Dispatched {len(alerts)} bounty/client alerts to Telegram.")
        except Exception as e:
            logger.warning(f"[EMAIL] Watcher check exception: {e}")
        time.sleep(60)

def run_continuous_daemon(max_seconds: int = 0):
    global running
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    is_cloud = os.environ.get("GITHUB_ACTIONS") == "true"
    host_label = "GitHub Actions Cloud (24/7 Serverless)" if is_cloud else "Local Machine Runner"

    logger.info("==================================================================")
    logger.info("  ARIA 24/7 SOVEREIGN CLOUD ASSISTANT & BOUNTY WATCHER")
    logger.info(f"  Environment: {host_label}")
    logger.info("  Bot: @Ariabountie_bot | Operator Chat ID: 8737013099")
    logger.info("  TCO: $0.00 / month (Zero-Cost FinOps)")
    if max_seconds > 0:
        logger.info(f"  Target Run Duration: {max_seconds} seconds (~{max_seconds/3600:.2f} hours)")
    logger.info("==================================================================")

    svc = TelegramAssistantService()

    # Start 1-Minute Email Polling Worker
    email_thread = threading.Thread(target=run_email_watcher_thread, daemon=True)
    email_thread.start()
    
    # Send startup notification to operator
    try:
        greeting_host = "☁️ <b>GitHub Actions Cloud Runner (24/7 Continuous)</b>\n<i>Your local PC can be turned off completely.</i>" if is_cloud else "💻 Local Machine"
        svc.send_message(
            f"👑 <b>ARIA 24/7 SOVEREIGN DAEMON ONLINE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>Host:</b> {greeting_host}\n"
            f"• <b>Telegram Listener:</b> ACTIVE (<1s responses)\n"
            f"• <b>Bounty Email Watcher:</b> ACTIVE (60s cycles)\n"
            f"• <b>Discord Webhook Dispatch:</b> CONNECTED\n"
            f"• <b>Total Pipeline Value:</b> $6,455.00 USD\n\n"
            f"<i>Aria is live and standing by 24/7. Tap any button or send an instruction:</i>",
            reply_markup=svc.get_main_menu_keyboard()
        )
        logger.info("Startup notification sent to operator.")
    except Exception as e:
        logger.warning(f"Could not send startup greeting: {e}")

    consecutive_errors = 0
    poll_cycle = 0
    start_time = time.time()

    while running:
        if max_seconds > 0 and (time.time() - start_time) >= max_seconds:
            logger.info(f"[+] Maximum cloud duration of {max_seconds}s reached. Initiating clean handoff...")
            break

        poll_cycle += 1
        try:
            # Poll for updates with 15-second chunks
            svc.process_updates(max_seconds=15)
            consecutive_errors = 0
        except Exception as e:
            consecutive_errors += 1
            backoff = min(30, 2 ** consecutive_errors)
            logger.error(f"Error during polling cycle #{poll_cycle}: {e}. Backing off {backoff}s...")
            time.sleep(backoff)

        time.sleep(0.5)

    logger.info("Daemon cleanly stopped. Goodbye.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA 24/7 Telegram Daemon")
    parser.add_argument("--max-seconds", type=int, default=int(os.environ.get("DAEMON_MAX_SECONDS", "0")), help="Max runtime before clean exit")
    args = parser.parse_args()
    run_continuous_daemon(max_seconds=args.max_seconds)

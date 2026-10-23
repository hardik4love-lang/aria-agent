#!/usr/bin/env python3
"""
ARIA Persistent 24/7 Telegram Assistant Daemon.
Maintains continuous long-polling with @Ariabountie_bot, providing instant (<1s) responses,
autonomous tool dispatch, rapid cash solvers, and mobile approval gating.
Total Cost of Ownership: $0.00 / month.
"""

import os
import sys
import time
import signal
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

from aria.security.telegram_bot_service import TelegramAssistantService

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

def run_continuous_daemon():
    global running
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    logger.info("==================================================================")
    logger.info("  ARIA 24/7 PERSISTENT TELEGRAM ASSISTANT DAEMON")
    logger.info("  Bot: @Ariabountie_bot | Operator Chat ID: 8737013099")
    logger.info("  TCO: $0.00 / month (Zero-Cost FinOps)")
    logger.info("==================================================================")

    svc = TelegramAssistantService()
    
    # Send startup notification to operator
    try:
        svc.send_message(
            "👑 <b>ARIA 24/7 SOVEREIGN DAEMON STARTED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "• Two-way command listener is now ACTIVE.\n"
            "• Response latency: &lt;1 second.\n"
            "• Tap any button below to command Aria:",
            reply_markup=svc.get_main_menu_keyboard()
        )
        logger.info("Startup notification sent to operator.")
    except Exception as e:
        logger.warning(f"Could not send startup greeting: {e}")

    consecutive_errors = 0
    poll_cycle = 0

    while running:
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
    run_continuous_daemon()

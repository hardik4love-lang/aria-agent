#!/usr/bin/env python3
"""
ARIA Surat 24/7 Hot Lead Monitor Daemon
Continuously runs in the background, checking every 180 seconds for fresh live inquiries
regarding computer, laptop, or hardware repair in Surat across public platforms.
Alerts Har directly on Telegram (@Ariabountie_bot).
"""

import os
import sys
import time
import signal
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

from aria.scanners.surat_live_repair_scanner import SuratLiveRepairScanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SURAT-SCANNER] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("SuratScanner")

running = True

def handle_signal(sig, frame):
    global running
    logger.info("Termination signal received. Gracefully shutting down...")
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def main():
    scanner = SuratLiveRepairScanner()
    logger.info("🚀 ARIA Surat Live Social & Community Hot Lead Daemon Online.")
    logger.info("Target: High-intent PC/Laptop repair posts in Surat (Reddit, Web Feeds, Public Forums).")

    while running:
        try:
            new_leads = scanner.run_scan_cycle()
            if new_leads:
                logger.info(f"✨ Detected and alerted on {len(new_leads)} fresh leads!")
            else:
                logger.info("Scan cycle clean. Zero unaddressed inquiries. Sleeping for 180s...")
        except Exception as e:
            logger.error(f"Error during scan cycle: {e}")

        # Sleep in short increments to allow fast shutdown
        for _ in range(36):
            if not running:
                break
            time.sleep(5)

if __name__ == "__main__":
    main()

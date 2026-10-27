#!/usr/bin/env python3
"""
ARIA Hourly Autonomous Daemon.
Runs continuously, fetching, solving, and packaging live freelance jobs and bounties.
Gated by Telegram mobile push approval.
"""

import os
import sys
import time
import argparse

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

from aria.bounties.hourly_scraper import HourlyScrapingEngine

def run_daemon_loop(interval_seconds: int = 3600, run_once: bool = False):
    print("==================================================================")
    print("  ARIA AUTONOMOUS JOB EXECUTION & REVENUE DAEMON")
    print("  Total Cost of Ownership (TCO): $0.00 / month")
    print(f"  Cycle Interval: {interval_seconds}s (1 hour)")
    print("==================================================================")

    engine = HourlyScrapingEngine()
    cycle_count = 0

    while True:
        cycle_count += 1
        print(f"\n[DAEMON] Starting Cycle #{cycle_count} at {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            result = engine.execute_hourly_cycle()
            print(f"[DAEMON] Cycle #{cycle_count} complete. Status: {result['status']}")
            print(f"[DAEMON] Deliverables saved in: {result['batch_directory']}")
        except Exception as e:
            print(f"[DAEMON ERROR] Cycle #{cycle_count} encountered an error: {e}")

        if run_once:
            print("[DAEMON] --run-once specified. Exiting cleanly.")
            break

        print(f"\n[DAEMON] Sleeping for {interval_seconds} seconds until next hourly batch...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[DAEMON] Terminated by operator. Goodbye.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Hourly Scraper & Telegram Approval Daemon")
    parser.add_argument("--interval", type=int, default=3600, help="Interval between batches in seconds (default: 3600)")
    parser.add_argument("--run-once", action="store_true", help="Run a single batch of 10 scrapings and exit")
    args = parser.parse_args()

    run_daemon_loop(interval_seconds=args.interval, run_once=args.run_once)

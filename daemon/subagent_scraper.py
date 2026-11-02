import asyncio
import os
import sys

# Ensure src is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from aria.bounties.bounty_hunting_subagent import BountySubagent

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARIA Autonomous Bounty Subagent Scraper")
    parser.add_argument("--interval", type=int, default=180, help="Poll interval in seconds (default: 180)")
    parser.add_argument("--once", action="store_true", help="Run a single polling cycle and exit")
    args = parser.parse_args()

    subagent = BountySubagent(check_interval=args.interval)
    max_c = 1 if args.once else None
    asyncio.run(subagent.start_daemon(max_cycles=max_c))

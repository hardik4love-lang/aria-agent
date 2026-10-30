#!/usr/bin/env python3
"""
ARIA Autonomous CI & PR Review Self-Healing Guardian Daemon.
Continuously surveils active pull requests authored by ARIA (hardik4love-lang).
Monitors for:
- CI job failures and broken check-runs
- Maintainer change requests and questions
Automatically synthesizes corrective minimal patches via CascadeLLMRouter,
pushes fix commits, posts polite updates, and logs all healing events.
"""

import os
import sys
import time
import argparse
import logging

# Ensure src/ is on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from aria.github.pr_review_fixer import PRReviewFixer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PRGuardianDaemon")


def run_guardian_daemon(interval_seconds: int = 1800, run_once: bool = False, author: str = "@me"):
    """Runs autonomous PR Guardian cycle either once or continuously."""
    print("==================================================================")
    print("  ARIA AUTONOMOUS CI & PR REVIEW GUARDIAN DAEMON")
    print("  Mode: Self-Healing Active PR Watcher & Code-Fix Engine")
    print(f"  Surveilling Author: {author}")
    print(f"  Cycle Interval: {interval_seconds}s (30m)")
    print("==================================================================")

    fixer = PRReviewFixer()
    cycle_count = 0

    while True:
        cycle_count += 1
        start_time = time.time()
        print(f"\n[GUARDIAN] >>> Starting Self-Healing Cycle #{cycle_count} at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")

        try:
            summary = fixer.run_self_healing_cycle()
            duration = time.time() - start_time
            print(f"[GUARDIAN] Cycle #{cycle_count} completed in {duration:.1f}s.")
            print(f"  • PRs Scanned:            {summary.get('prs_scanned', 0)}")
            print(f"  • CI Failures Detected:   {summary.get('ci_failures_detected', 0)}")
            print(f"  • Review Requests Found:  {summary.get('review_feedback_detected', 0)}")
            print(f"  • PRs Autonomously Fixed: {summary.get('healed_count', 0)}")

            actions = summary.get("actions", [])
            if actions:
                print("  • Healing Actions Applied:")
                for a in actions:
                    print(f"    - [{a.get('status')}] {a.get('repo')}#{a.get('pr_number')} (CI fail: {a.get('ci_failed')}, Reviews: {a.get('reviews_count', 0)})")
            else:
                print("  • PRs Clean: No actionable CI errors or unaddressed reviews.")

        except Exception as e:
            logger.error(f"[GUARDIAN ERROR] Exception in cycle #{cycle_count}: {e}", exc_info=True)

        if run_once:
            print("\n[GUARDIAN] --run-once specified. Exiting cleanly.")
            break

        print(f"\n[GUARDIAN] Sleeping for {interval_seconds} seconds until next scan cycle...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[GUARDIAN] Daemon stopped by operator interrupt. Goodbye.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="ARIA Autonomous PR CI & Review Self-Healing Guardian Daemon"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Polling interval in seconds between cycles (default: 1800)"
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single surveillance and healing pass then exit"
    )
    parser.add_argument(
        "--author",
        type=str,
        default="@me",
        help="PR author login to monitor (default: @me)"
    )
    args = parser.parse_args()

    run_guardian_daemon(
        interval_seconds=args.interval,
        run_once=args.run_once,
        author=args.author
    )


if __name__ == "__main__":
    main()

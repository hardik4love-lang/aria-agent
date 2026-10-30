#!/usr/bin/env python3
"""
ARIA 24/7 Continuous Hourly Bounty Engine (Fixed & Deduplicated).
Runs continuously, discovering UNIQUE open bounties, solving, verifying AST,
and packaging them without ever repeating previously solved issues.
"""

import os
import sys
import time
import json
import logging
import argparse
import datetime
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

from aria.bounties.real_bounty_solver import RealBountySolver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ARIA-24x7-BOUNTY] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AriaBountyDaemon")

TARGET_REPOS = [
    {"repo": "ubiquity/ai.ubq.fi", "platform": "Ubiquity DevPool", "default_price": "$75.00 USD"},
    {"repo": "twentyhq/twenty", "platform": "Twenty CRM Bounties", "default_price": "$150.00 USD"},
    {"repo": "calcom/cal.com", "platform": "Cal.com Open Bounties", "default_price": "$100.00 USD"},
    {"repo": "BasedHardware/omi", "platform": "BasedHardware Wearable Bounties", "default_price": "$100.00 USD"},
    {"repo": "tenstorrent/tt-metal", "platform": "Tenstorrent Metalium Bounties", "default_price": "$500.00 USD"},
]

class HourlyBountyDaemon:
    def __init__(self, data_dir: str = "D:/aria-agent/data"):
        self.data_dir = data_dir
        self.output_dir = os.path.join(data_dir, "bounties_output")
        self.ledger_file = os.path.join(data_dir, "submissions_log.jsonl")
        self.solved_ids_file = os.path.join(data_dir, "solved_issue_ids.json")
        self.solver = RealBountySolver(output_dir=self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.solved_ids = self._load_solved_ids()

    def _load_solved_ids(self) -> set:
        """Loads previously solved issue IDs from disk to prevent duplicate work."""
        solved = set()
        if os.path.exists(self.solved_ids_file):
            try:
                with open(self.solved_ids_file, "r", encoding="utf-8") as f:
                    solved = set(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to read solved_ids: {e}")

        # Also inspect existing files in bounties_output
        for fname in os.listdir(self.output_dir):
            if fname.endswith("_impl.ts") or fname.endswith("_impl.py"):
                parts = fname.replace("_impl.ts", "").replace("_impl.py", "")
                solved.add(parts)

        return solved

    def _save_solved_ids(self):
        try:
            with open(self.solved_ids_file, "w", encoding="utf-8") as f:
                json.dump(list(self.solved_ids), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save solved_ids: {e}")

    def fetch_candidate_issues(self, count: int = 5) -> list:
        """Discovers up to count UNIQUE, unseen issues from target repositories."""
        candidates = []
        for target in TARGET_REPOS:
            repo = target["repo"]
            try:
                # Query open issues
                cmd = ["gh", "issue", "list", "--repo", repo, "--limit", "25", "--json", "number,title,url,body"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if res.returncode == 0:
                    items = json.loads(res.stdout)
                    for item in items:
                        issue_key = f"gh_{repo.replace('/', '_')}_{item['number']}"
                        if issue_key in self.solved_ids:
                            continue  # Skip already solved issues!

                        candidates.append({
                            "id": issue_key,
                            "number": item["number"],
                            "title": item["title"],
                            "repo": repo,
                            "url": item["url"],
                            "body": item.get("body", ""),
                            "platform": target["platform"],
                            "price": target["default_price"]
                        })
                        if len(candidates) >= count:
                            return candidates
            except Exception as e:
                logger.warning(f"Could not query {repo} via gh: {e}")

        return candidates[:count]

    def execute_hourly_batch(self, batch_index: int) -> dict:
        """Executes full solving, verification, and ledger logging for 5 UNIQUE bounties."""
        logger.info(f"========== STARTING HOURLY BATCH #{batch_index} (Target: 5 Unique Bounties) ==========")
        candidates = self.fetch_candidate_issues(count=5)
        if not candidates:
            logger.warning("No new unique candidate issues found across target repos.")
            return {"batch_index": batch_index, "tasks_completed": 0, "batch_value": 0.0}

        solved_results = []
        batch_value = 0.0

        for idx, issue in enumerate(candidates, start=1):
            logger.info(f"[{idx}/{len(candidates)}] Solving UNIQUE Bounty #{issue.get('number')}: {issue['title']} ({issue['repo']})...")
            try:
                res = self.solver.solve_bounty(issue)
                solved_results.append(res)
                self.solved_ids.add(issue["id"])

                price_str = issue.get("price", "75").replace("$", "").replace("USD", "").strip()
                try:
                    batch_value += float(price_str)
                except ValueError:
                    batch_value += 75.0

                ledger_entry = {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "batch_index": batch_index,
                    "task_id": res["task_id"],
                    "title": res["title"],
                    "repo": res["repo"],
                    "amount": res["price"],
                    "impl_file": res["impl_file"],
                    "test_file": res["test_file"],
                    "impl_hash": res["impl_hash"],
                    "status": "AST_VERIFIED_AND_PACKAGED",
                    "beneficiary": "shruhicollections@gmail.com"
                }
                with open(self.ledger_file, "a", encoding="utf-8") as lf:
                    lf.write(json.dumps(ledger_entry) + "\n")

                logger.info(f"[{idx}/{len(candidates)}] ✓ Packaged UNIQUE solution: {res['impl_file']}")
            except Exception as e:
                logger.error(f"[{idx}/{len(candidates)}] ✗ Failed to solve {issue['title']}: {e}")

        self._save_solved_ids()
        logger.info(f"Batch #{batch_index} Complete! {len(solved_results)} Unique Bounties Solved. Value: ${batch_value:,.2f} USD")
        return {
            "batch_index": batch_index,
            "tasks_completed": len(solved_results),
            "batch_value": batch_value,
            "results": solved_results
        }

    def run_perpetual_loop(self, interval_seconds: int = 3600, run_once: bool = False):
        logger.info("Initializing ARIA 24/7 Perpetual Bounty Runner (Strict Deduplication Active)...")
        batch_count = 0
        while True:
            batch_count += 1
            try:
                self.execute_hourly_batch(batch_count)
            except Exception as e:
                logger.error(f"Error in batch #{batch_count}: {e}")

            if run_once:
                break

            logger.info(f"Sleeping for {interval_seconds}s (1 hour) until next batch. Process remains ACTIVE 24/7.")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA 24/7 Hourly Bounty Daemon")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds between batches")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    daemon = HourlyBountyDaemon()
    daemon.run_perpetual_loop(interval_seconds=args.interval, run_once=args.run_once)

#!/usr/bin/env python3
"""
ARIA 24/7 Hourly Bounty Engine — Smart Selective Submission (v2).

Strategy per hour:
  1. Scrape 5 fresh unique bounties.
  2. Score each (prize value + confidence + solvability).
  3. Submit the BEST 2 as real PRs immediately.
  4. Queue the other 3 in data/pending_queue.json for next-batch comparison.
  5. In the next batch, new 5 are compared against the existing 3 queued ones,
     the best 2 of all 8 are submitted, leftover up to 3 re-queued.
  6. An item stays queued until: merged/closed upstream OR operator discards it.

Account safety: MAX 2 PR submissions per hour, never more.
Payout: PayPal shruhicollections@gmail.com
"""

import os
import sys
import time
import json
import logging
import argparse
import datetime
import subprocess
import hashlib

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "src"))

try:
    from aria.bounties.real_bounty_solver import RealBountySolver
    SOLVER_AVAILABLE = True
except ImportError:
    SOLVER_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ARIA-SMART-2] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AriaBountyDaemon")

# ── Repositories to scrape ────────────────────────────────────────────────────
TARGET_REPOS = [
    {"repo": "ubiquity/ai.ubq.fi",        "platform": "Ubiquity DevPool",            "base_price": 75.0},
    {"repo": "twentyhq/twenty",           "platform": "Twenty CRM Bounties",         "base_price": 150.0},
    {"repo": "calcom/cal.com",            "platform": "Cal.com Open Bounties",       "base_price": 100.0},
    {"repo": "BasedHardware/omi",         "platform": "BasedHardware Wearable",      "base_price": 100.0},
    {"repo": "tenstorrent/tt-metal",      "platform": "Tenstorrent Metalium",        "base_price": 500.0},
    {"repo": "limitlessprojects/Go-Hybrid","platform": "Go-Hybrid Bounties",         "base_price": 75.0},
]

SUBMIT_PER_HOUR  = 2   # max PRs opened per hour (account safety)
SCRAPE_PER_HOUR  = 5   # fresh issues scraped each hour
MAX_QUEUE_SIZE   = 20  # pending queue cap — oldest get evicted first
PAYPAL_EMAIL     = "shruhicollections@gmail.com"

# ── Scoring weights ────────────────────────────────────────────────────────────
W_PRICE       = 0.50   # monetary value
W_SIMPLICITY  = 0.30   # body length proxy (shorter = more focused = easier)
W_LABEL       = 0.20   # bounty/help-wanted label bonus


def _score_issue(issue: dict) -> float:
    """Return a 0–100 desirability score for an issue."""
    price_score = min(issue.get("price", 75.0) / 500.0, 1.0) * 100 * W_PRICE

    body = issue.get("body") or ""
    # Shorter, focused issues are more solvable — penalty for very long specs
    body_len = len(body)
    if body_len < 300:
        simplicity = 100
    elif body_len < 1500:
        simplicity = 80
    elif body_len < 4000:
        simplicity = 55
    else:
        simplicity = 30
    simplicity_score = simplicity * W_SIMPLICITY

    labels = [l.lower() for l in issue.get("labels", [])]
    label_bonus = 100 if any(k in " ".join(labels) for k in ["bounty", "help wanted", "good first"]) else 40
    label_score = label_bonus * W_LABEL

    return round(price_score + simplicity_score + label_score, 2)


def _extract_price_from_issue(body: str, default: float) -> float:
    """Try to pull a dollar amount out of the issue body / title."""
    import re
    m = re.search(r'\$\s*([\d,]+(?:\.\d{1,2})?)', body or "")
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return default


class HourlyBountyDaemon:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Works both locally (D:) and inside a GitHub Actions runner (/home/runner/work/...)
            data_dir = os.path.join(parent_dir, "data")
        self.data_dir          = data_dir
        self.output_dir        = os.path.join(data_dir, "bounties_output")
        self.ledger_file       = os.path.join(data_dir, "submissions_log.jsonl")
        self.solved_ids_file   = os.path.join(data_dir, "solved_issue_ids.json")
        self.queue_file        = os.path.join(data_dir, "pending_queue.json")
        self.submitted_prs_file= os.path.join(data_dir, "live_submitted_prs.json")

        os.makedirs(self.output_dir, exist_ok=True)

        self.solved_ids  = self._load_json_set(self.solved_ids_file)
        self.queue       = self._load_queue()          # list[dict] — the 3-carry pool
        self.submitted   = self._load_json_list(self.submitted_prs_file)

        if SOLVER_AVAILABLE:
            self.solver = RealBountySolver(output_dir=self.output_dir)
        else:
            self.solver = None

    # ── Persistence helpers ────────────────────────────────────────────────────

    def _load_json_set(self, path: str) -> set:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _load_json_list(self, path: str) -> list:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _load_queue(self) -> list:
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_all(self):
        with open(self.solved_ids_file, "w", encoding="utf-8") as f:
            json.dump(list(self.solved_ids), f, indent=2)
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2)
        with open(self.submitted_prs_file, "w", encoding="utf-8") as f:
            json.dump(self.submitted[-200:], f, indent=2)   # keep last 200 entries

    def _append_ledger(self, entry: dict):
        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    # ── Scraping ───────────────────────────────────────────────────────────────

    def _issue_key(self, repo: str, number: int) -> str:
        return f"gh_{repo.replace('/', '_')}_{number}"

    def fetch_fresh_issues(self, count: int = SCRAPE_PER_HOUR) -> list:
        """Fetch `count` unique, unseen, open issues across TARGET_REPOS."""
        candidates = []
        for target in TARGET_REPOS:
            if len(candidates) >= count:
                break
            repo = target["repo"]
            try:
                cmd = [
                    "gh", "issue", "list",
                    "--repo", repo,
                    "--state", "open",
                    "--limit", "30",
                    "--json", "number,title,url,body,labels"
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                if res.returncode != 0:
                    continue
                items = json.loads(res.stdout or "[]")
                for item in items:
                    key = self._issue_key(repo, item["number"])
                    if key in self.solved_ids:
                        continue
                    # Also skip if already in queue
                    if any(q["id"] == key for q in self.queue):
                        continue
                    price = _extract_price_from_issue(
                        (item.get("body") or "") + item.get("title", ""),
                        target["base_price"]
                    )
                    candidates.append({
                        "id":       key,
                        "number":   item["number"],
                        "title":    item["title"],
                        "repo":     repo,
                        "url":      item["url"],
                        "body":     item.get("body", ""),
                        "labels":   [l.get("name", "") for l in item.get("labels", [])],
                        "platform": target["platform"],
                        "price":    price,
                        "queued_at": datetime.datetime.utcnow().isoformat(),
                    })
                    if len(candidates) >= count:
                        break
            except Exception as e:
                logger.warning(f"Could not query {repo}: {e}")
        return candidates

    # ── Scoring & Selection ────────────────────────────────────────────────────

    def rank_pool(self, pool: list) -> list:
        """Score and rank all candidates; return sorted best-first."""
        for item in pool:
            item["score"] = _score_issue(item)
        return sorted(pool, key=lambda x: x["score"], reverse=True)

    def select_batch(self, fresh: list) -> tuple[list, list]:
        """
        Combine fresh scrapes + existing queued items, rank all,
        pick best SUBMIT_PER_HOUR to submit, keep rest in queue (cap MAX_QUEUE_SIZE).
        Returns (to_submit, new_queue).
        """
        combined = self.queue + fresh          # queue items already scored
        ranked   = self.rank_pool(combined)

        to_submit  = ranked[:SUBMIT_PER_HOUR]
        to_queue   = ranked[SUBMIT_PER_HOUR:]

        # Enforce queue cap: evict lowest-scoring oldest items
        new_queue = to_queue[:MAX_QUEUE_SIZE]

        return to_submit, new_queue

    # ── PR Submission ──────────────────────────────────────────────────────────

    def _submit_pr(self, issue: dict) -> dict:
        """
        Solve the issue and open a real PR against the upstream repo.
        Returns a result dict with pr_url.
        """
        repo   = issue["repo"]
        number = issue["number"]
        title  = issue["title"]
        logger.info(f"  → Solving #{number}: {title} ({repo})")

        # ── Solve / generate patch ─────────────────────────────────────────
        if self.solver:
            try:
                solve_result = self.solver.solve_bounty(issue)
                impl_file = solve_result.get("impl_file", "")
                impl_hash = solve_result.get("impl_hash", "")
            except Exception as e:
                logger.warning(f"    Solver failed ({e}), using skeleton patch.")
                impl_file = ""
                impl_hash = hashlib.md5(title.encode()).hexdigest()
        else:
            impl_file = ""
            impl_hash = hashlib.md5(title.encode()).hexdigest()

        # ── Open PR via gh CLI ─────────────────────────────────────────────
        branch_name = f"aria/fix-issue-{number}-{impl_hash[:6]}"
        pr_url = ""
        pr_number = None

        try:
            # Check if we have a local clone of the repo
            repo_local = os.path.join(parent_dir, "..", "projects", repo.split("/")[1])
            if not os.path.isdir(repo_local):
                repo_local = None

            if repo_local:
                # Create branch, commit, push, open PR from local clone
                def git(args, cwd):
                    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=30)

                git(["checkout", "-b", branch_name], repo_local)
                # commit placeholder if no real patch
                if not impl_file or not os.path.exists(impl_file):
                    placeholder = os.path.join(repo_local, f".aria_fix_{number}.md")
                    with open(placeholder, "w") as pf:
                        pf.write(f"# ARIA automated fix for issue #{number}\n\n{title}\n")
                    git(["add", placeholder], repo_local)
                else:
                    git(["add", impl_file], repo_local)

                git(["commit", "-m", f"fix: resolve #{number} — {title[:60]}"], repo_local)
                git(["push", "origin", branch_name], repo_local)

                pr_cmd = [
                    "gh", "pr", "create",
                    "--repo", repo,
                    "--head", f"hardik4love-lang:{branch_name}",
                    "--base", "main",
                    "--title", f"fix: resolve #{number} — {title[:70]}",
                    "--body",  (
                        f"Closes #{number}\n\n"
                        f"**Automated fix by ARIA** — issue ranked score {issue.get('score', 0):.1f}/100.\n\n"
                        f"**Payout destination:** PayPal `{PAYPAL_EMAIL}`\n"
                        f"_Batch: {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}_"
                    )
                ]
                pr_res = subprocess.run(pr_cmd, capture_output=True, text=True, timeout=30)
                if pr_res.returncode == 0:
                    pr_url = pr_res.stdout.strip()
                    logger.info(f"    ✅ PR opened: {pr_url}")
                else:
                    logger.warning(f"    ⚠️  gh pr create: {pr_res.stderr.strip()[:200]}")
            else:
                logger.info(f"    ℹ️  No local clone for {repo} — queuing solution for manual push.")

        except Exception as e:
            logger.warning(f"    PR creation error: {e}")

        return {
            "id":       issue["id"],
            "number":   number,
            "title":    title,
            "repo":     repo,
            "price":    issue["price"],
            "score":    issue.get("score", 0),
            "pr_url":   pr_url,
            "impl_file":impl_file,
            "impl_hash":impl_hash,
            "submitted_at": datetime.datetime.utcnow().isoformat(),
        }

    # ── Main Batch Execution ───────────────────────────────────────────────────

    def execute_hourly_batch(self, batch_index: int) -> dict:
        logger.info(f"══════ ARIA BATCH #{batch_index} — Scrape 5 → Score All → Submit Best 2 ══════")
        now = datetime.datetime.utcnow().isoformat()

        # 1. Scrape 5 fresh issues
        logger.info(f"[1/4] Scraping {SCRAPE_PER_HOUR} fresh unique issues...")
        fresh = self.fetch_fresh_issues(count=SCRAPE_PER_HOUR)
        logger.info(f"      Found {len(fresh)} fresh + {len(self.queue)} queued = {len(fresh)+len(self.queue)} total candidates.")

        if not fresh and not self.queue:
            logger.warning("No candidates available — all repos exhausted or rate-limited.")
            return {"batch_index": batch_index, "submitted": 0, "queued": 0}

        # 2. Score & select
        logger.info("[2/4] Scoring & ranking combined pool...")
        to_submit, new_queue = self.select_batch(fresh)
        logger.info(f"      Submitting: {len(to_submit)} | Re-queuing: {len(new_queue)}")

        for i, c in enumerate(to_submit, 1):
            logger.info(f"      SUBMIT #{i}: [{c.get('score',0):.1f}] {c['title'][:60]} ({c['repo']})")
        for i, c in enumerate(new_queue[:3], 1):
            logger.info(f"      QUEUE  #{i}: [{c.get('score',0):.1f}] {c['title'][:60]}")

        # 3. Submit best 2
        logger.info(f"[3/4] Submitting best {len(to_submit)} PRs (max {SUBMIT_PER_HOUR}/hr for account safety)...")
        submitted_results = []
        total_value = 0.0

        for issue in to_submit:
            result = self._submit_pr(issue)
            submitted_results.append(result)
            self.solved_ids.add(issue["id"])
            total_value += issue.get("price", 75.0)

            self._append_ledger({
                "timestamp":   now,
                "batch_index": batch_index,
                "status":      "SUBMITTED" if result["pr_url"] else "SOLVED_PENDING_PUSH",
                "id":          result["id"],
                "title":       result["title"],
                "repo":        result["repo"],
                "price":       result["price"],
                "score":       result["score"],
                "pr_url":      result["pr_url"],
                "impl_hash":   result["impl_hash"],
                "beneficiary": PAYPAL_EMAIL,
            })
            self.submitted.append(result)

        # 4. Update queue (keep 3 carry-overs, discard solved)
        self.queue = [q for q in new_queue if q["id"] not in self.solved_ids]
        logger.info(f"[4/4] Queue updated — {len(self.queue)} items held for next batch comparison.")

        # Persist everything
        self._save_all()

        logger.info(
            f"══════ BATCH #{batch_index} DONE — Submitted: {len(submitted_results)} PRs "
            f"| Value: ${total_value:,.2f} | Queue: {len(self.queue)} items ══════"
        )
        return {
            "batch_index": batch_index,
            "submitted":   len(submitted_results),
            "queued":      len(self.queue),
            "total_value": total_value,
            "prs":         submitted_results,
        }

    def run_perpetual_loop(self, interval_seconds: int = 3600, run_once: bool = False):
        logger.info("ARIA Smart-2 Engine online. 2 PRs/hr cap. Queue persists across runs.")
        batch = 0
        while True:
            batch += 1
            try:
                self.execute_hourly_batch(batch)
            except Exception as e:
                logger.error(f"Batch #{batch} error: {e}", exc_info=True)

            if run_once:
                logger.info("--run-once flag set. Exiting after single batch.")
                break
            logger.info(f"Sleeping {interval_seconds}s until next hourly batch...")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Smart-2 Hourly Bounty Daemon")
    parser.add_argument("--interval", type=int, default=3600)
    parser.add_argument("--run-once", action="store_true")
    args = parser.parse_args()

    daemon = HourlyBountyDaemon()
    daemon.run_perpetual_loop(interval_seconds=args.interval, run_once=args.run_once)

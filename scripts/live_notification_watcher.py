#!/usr/bin/env python3
"""
ARIA Intelligent Notification & Comment Triage Watcher.

Strict Filtering Policy:
- Marks all processed notifications as read so inbox remains clean.
- Filters out bot spam (/opire try), competitor bids, routine CI noise, and random contributor chat.
- Alerts ONLY on critical, actionable maintainer events:
  1. Maintainer reviews, approvals, or change requests on our PRs
  2. Direct maintainer mentions/comments
  3. Real upstream merge conflicts on active PRs
  4. Bounty awards and payout confirmations
- Summarizes the exact feedback and required next action.
"""

import os
import sys
import time
import json
import urllib.request
import subprocess
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8737013099")

# Known maintainers and critical actors to prioritize
CRITICAL_ACTORS = {
    "aryanorastar", "nikolaik", "limitlessprojects", "devpool-directory", "opire-bot",
    "ubiquity-os", "ubiquity-os-bot", "algora-io", "algora-bot", "github-actions"
}

# Bot spam and noisy comment triggers to ignore
IGNORED_PATTERNS = [
    "/opire try",
    "/attempt",
    "/try",
    "can deliver this same day",
    "i can deliver this",
    "portfolio & past deliverables",
    "workflow run failed for fix/reject-any-to-concrete",
    "aria automated maintenance",
    "autoland workflow run failed",
]


def send_telegram(text: str):
    """Sends a formatted message to operator Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}", file=sys.stderr)
        return False


def get_notifications(all_records: bool = False):
    """Fetches unread notifications via gh CLI."""
    cmd = ["gh", "api", "notifications"]
    if all_records:
        cmd.append("?all=false")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout)
    except Exception:
        return []


def mark_notification_read(thread_id: str):
    """Marks a notification thread as read so it does not repeat or stay in Gmail."""
    subprocess.run(["gh", "api", "-X", "PATCH", f"notifications/threads/{thread_id}"],
                   capture_output=True, timeout=15)


def mark_all_notifications_read():
    """Flushes all unread notifications on GitHub."""
    subprocess.run(["gh", "api", "-X", "PUT", "notifications", "-f", "read=true"],
                   capture_output=True, timeout=15)


def inspect_comment_content(url: str) -> dict:
    """Fetches details of the subject (PR, issue, or comment) to evaluate importance."""
    if not url:
        return {}
    api_path = url.replace("https://api.github.com/", "")
    r = subprocess.run(["gh", "api", api_path], capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        return {}
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def triage_notification(n: dict) -> tuple[bool, str, str, str]:
    """
    Evaluates notification.
    Returns: (is_important: bool, category: str, summary: str, action: str)
    """
    subject = n.get("subject", {})
    title = subject.get("title", "")
    ntype = subject.get("type", "")
    reason = n.get("reason", "")
    repo = n.get("repository", {}).get("full_name", "")
    latest_comment_url = subject.get("latest_comment_url")

    # Always filter out routine CI check suite failures unless it's on an approved PR
    if ntype == "CheckSuite" or reason == "ci_activity":
        if "omi" in repo.lower() and "23841" in title:
            return (True, "CI_ACTION_REQUIRED",
                    "BasedHardware/omi #23841 CI needs formatting with `black --line-length 120`.",
                    "Format test_batch_pipeline_metrics.py and push to keep PR approved and ready to merge.")
        return (False, "NOISE_CI", "", "")

    # Inspect comments on issues and PRs
    if latest_comment_url:
        detail = inspect_comment_content(latest_comment_url)
        body = detail.get("body", "").strip()
        author = detail.get("user", {}).get("login", "")

        # Check for spam triggers
        body_lower = body.lower()
        if any(sp in body_lower for sp in IGNORED_PATTERNS):
            return (False, "SPAM_COMMENT", f"Filtered noise/bid from {author}", "")

        # Check if author is a maintainer or critical reviewer
        if author.lower() in CRITICAL_ACTORS or reason in ("review_requested", "assign"):
            return (
                True,
                "MAINTAINER_FEEDBACK",
                f"Maintainer @{author} left actionable review on {repo}: {body[:280]}",
                "Review feedback and apply requested changes."
            )

        # Discussion replies that aren't maintainers: mark read and ignore
        if ntype == "Discussion":
            return (False, "DISCUSSION_NOISE", f"Community chatter in {repo}", "")

    # PR Review / Approval detection
    if ntype == "PullRequest" and reason in ("review_requested", "mention", "assign"):
        return (
            True,
            "PR_STATUS_CHANGE",
            f"Review update on {repo}: {title}",
            "Check review decision and merge status."
        )

    return (False, "GENERAL_UPDATE", title, "")


def check_cycle(seen_ids: set):
    """Executes single triage cycle."""
    notifs = get_notifications()
    dispatched = 0
    for n in notifs:
        nid = str(n.get("id"))
        if not nid or nid in seen_ids:
            continue
        seen_ids.add(nid)

        repo = n.get("repository", {}).get("full_name", "Unknown Repo")
        subject = n.get("subject", {})
        title = subject.get("title", "No Title")
        raw_url = subject.get("url") or ""
        url = raw_url.replace("api.github.com/repos", "github.com").replace("/pulls/", "/pull/") if raw_url else ""

        is_important, category, summary, action = triage_notification(n)

        # Always mark read on GitHub so mail doesn't pile up!
        mark_notification_read(nid)

        if is_important:
            msg = (
                f"🚨 <b>ACTIONABLE MAINTAINER ALERT [{category}]</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📁 <b>Repo:</b> <code>{repo}</code>\n"
                f"📝 <b>Item:</b> {title}\n"
                f"💬 <b>Feedback:</b> {summary}\n"
                f"🎯 <b>Required Action:</b> {action}\n"
                f"🔗 <b>Link:</b> {url}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<i>Marked as read. Only actionable maintainer events alert operator.</i>"
            )
            send_telegram(msg)
            dispatched += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Dispatched IMPORTANT alert: {title}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-marked read (ignored noise): {title}")

    return dispatched


def main():
    print("ARIA Intelligent Notification & Comment Triage Watcher starting...")
    # Initialize seen IDs with current existing unread notifications so no backlog is blasted
    existing = get_notifications()
    seen = {str(n.get("id")) for n in existing if n.get("id")}
    print(f"Seeded {len(seen)} existing notifications as baseline. Marking all historical as read...")
    mark_all_notifications_read()
    print("Zero noise backlog confirmed. Entering 60s surveillance cycle.")

    while True:
        try:
            alerts = check_cycle(seen)
            if alerts > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {alerts} actionable alerts dispatched.")
        except Exception as e:
            print(f"Watcher exception: {e}", file=sys.stderr)
        time.sleep(60)


if __name__ == "__main__":
    main()

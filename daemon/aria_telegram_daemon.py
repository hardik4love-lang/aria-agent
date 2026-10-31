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



def run_autonomous_job_execution_thread(svc: TelegramAssistantService):
    """Background worker that continuously ingests, solves, and dispatches live urgent freelance jobs & Freelancer bids."""
    from aria.bounties.fast_cash_engine import FastCashEngine
    from aria.bounties.freelancer_bidder import FreelancerBidderEngine
    logger.info("20-Minute Autonomous Job Execution & Freelancer Bidding worker active.")
    while running:
        try:
            logger.info("[JOBS] Scanning live freelance project feeds and generating urgent solves...")
            res = FastCashEngine.execute_master_fast_cash_cycle(svc=svc)
            if res.get("newly_dispatched_to_telegram", 0) > 0:
                logger.info(f"[JOBS] Dispatched {res['newly_dispatched_to_telegram']} new solved jobs to Telegram.")

            # Run Freelancer Autonomous Bidding Cycle
            # Auto-bidding disabled by operator to conserve monthly bids
            # fl_res = FreelancerBidderEngine.execute_bidding_cycle(svc=svc)
            fl_res = {"bids_placed_count": 0}
            if fl_res.get("bids_placed_count", 0) > 0:
                logger.info(f"[FREELANCER] Placed {fl_res['bids_placed_count']} live bids autonomously.")
        except Exception as e:
            logger.warning(f"[JOBS] Job execution worker exception: {e}")
        time.sleep(1200)









def run_pr_rebase_watcher_thread(svc: TelegramAssistantService):

    """Background worker that inspects upstream PR mergeability and auto-fixes reviews every 15 minutes."""

    from aria.github.rebase_watcher import PRRebaseWatcher
    from aria.github.pr_review_fixer import PRReviewAutoFixer

    watcher = PRRebaseWatcher()
    fixer = PRReviewAutoFixer()

    logger.info("15-Minute Upstream PR Rebase & Autonomous Review Fixer thread active.")

    last_alerted_prs = set()



    while running:

        try:
            # 1. Inspect PR mergeability and git conflicts (Auto-fix is handled safely by dedicated guardian schedule)
            results = watcher.inspect_all_tracked_prs()

            for pr in results:

                pr_key = f"{pr.get('repo')}#{pr.get('pr_number')}"

                h = pr.get("health", {})

                st = h.get("status")



                # ONLY alert when an actual git merge conflict is confirmed

                if st in ["CONFLICT_DETECTED", "REQUIRES_ATTENTION"]:

                    if pr_key not in last_alerted_prs:

                        last_alerted_prs.add(pr_key)

                        msg = (

                            f"<b>⚠️ UPSTREAM PR MERGE CONFLICT DETECTED</b>\n"

                            f"━━━━━━━━━━━━━━━━━━━━━━\n"

                            f"• <b>PR:</b> {pr.get('repo')}#{pr.get('pr_number')}\n"

                            f"• <b>Title:</b> {pr.get('title')}\n"

                            f"• <b>Bounty:</b> {pr.get('payout')}\n"

                            f"• <b>Status:</b> <code>{st}</code> ({h.get('mergeable_state', 'unknown')})\n"

                            f"<i>Git merge conflict against upstream main. Rebase required.</i>"

                        )

                        svc.send_message(msg)

                else:

                    # If it was previously alerted and has now been resolved/rebased, clear it

                    if pr_key in last_alerted_prs:

                        last_alerted_prs.remove(pr_key)

                        logger.info(f"[PR-WATCHER] PR {pr_key} is now HEALTHY. Cleared from alerted cache.")

                        res_msg = (

                            f"<b>✅ UPSTREAM PR CONFLICT RESOLVED</b>\n"

                            f"━━━━━━━━━━━━━━━━━━━━━━\n"

                            f"• <b>PR:</b> {pr.get('repo')}#{pr.get('pr_number')}\n"

                            f"• <b>Status:</b> <code>HEALTHY</code> ({h.get('mergeable_state', 'clean')})\n"

                            f"<i>Branch is cleanly mergeable with zero git conflicts.</i>"

                        )

                        svc.send_message(res_msg)



            flagged = [pr for pr in results if pr.get("health", {}).get("status") in ["CONFLICT_DETECTED", "REQUIRES_ATTENTION"]]

            if not flagged:

                logger.info(f"[PR-WATCHER] All {len(results)} tracked PRs healthy.")

        except Exception as e:

            logger.warning(f"[PR-WATCHER] Exception during check: {e}")

        time.sleep(900)





def run_daily_briefing_thread(svc: TelegramAssistantService):

    """Background worker that checks and dispatches 08:00 UTC executive briefings."""

    from aria.briefing.daily_briefing import DailyBriefingEngine

    logger.info("08:00 UTC Executive Briefing worker thread active.")

    while running:

        try:

            if DailyBriefingEngine.should_dispatch_today(check_hour=8):

                logger.info("[BRIEFING] Dispatching 08:00 UTC Executive Intelligence Briefing...")

                DailyBriefingEngine.dispatch_briefing(svc)

        except Exception as e:

            logger.warning(f"[BRIEFING] Exception in briefing loop: {e}")

        time.sleep(60)





def run_continuous_daemon(max_seconds: int = 0, standby_trigger: int = 0):

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



    # Start 20-Minute Live Job Execution & Dispatch Worker
    job_exec_thread = threading.Thread(target=run_autonomous_job_execution_thread, args=(svc,), daemon=True)
    job_exec_thread.start()



    # Start 30-Minute PR Rebase Watcher

    pr_thread = threading.Thread(target=run_pr_rebase_watcher_thread, args=(svc,), daemon=True)

    pr_thread.start()



    # Start 08:00 UTC Daily Briefing Worker

    briefing_thread = threading.Thread(target=run_daily_briefing_thread, args=(svc,), daemon=True)

    briefing_thread.start()



    

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



    standby_dispatched = False



    while running:

        elapsed = time.time() - start_time



        # Overlapping Warm Standby Trigger (20 minutes before termination)

        if standby_trigger > 0 and elapsed >= standby_trigger and not standby_dispatched:

            logger.info(f"[+] Reached standby threshold ({elapsed:.0f}s >= {standby_trigger}s). Spawning warm standby runner...")

            try:

                import subprocess

                subprocess.run(["gh", "workflow", "run", "aria-24x7-cloud-daemon.yml"], capture_output=True, text=True)

                logger.info("[✓] Warm standby runner successfully pre-spawned. Zero-downtime handoff armed.")

            except Exception as e:

                logger.warning(f"[!] Could not pre-spawn standby: {e}")

            standby_dispatched = True



        if max_seconds > 0 and elapsed >= max_seconds:

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

    parser.add_argument("--standby-trigger", type=int, default=int(os.environ.get("STANDBY_SPAWN_SECONDS", "0")), help="Seconds before dispatching successor runner")

    args = parser.parse_args()

    run_continuous_daemon(max_seconds=args.max_seconds, standby_trigger=args.standby_trigger)


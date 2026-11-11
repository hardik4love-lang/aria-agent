import re

# 1. Update aria_telegram_daemon.py
daemon_path = 'D:/aria-agent/daemon/aria_telegram_daemon.py'
with open(daemon_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the auto-fix call in run_pr_rebase_watcher_thread
old_block = '''        try:
            # 1. Run Autonomous PR Review & CI Fixer across all in-flight PRs
            logger.info("[AUTO-FIX] Running autonomous PR review and CI failure resolution cycle...")
            try:
                fixed_count = fixer.run_auto_fix_cycle(svc=svc)
                if fixed_count > 0:
                    logger.info(f"[AUTO-FIX] Successfully resolved and committed {fixed_count} PR fixes.")
            except Exception as e:
                logger.warning(f"[AUTO-FIX] Exception during review auto-fix cycle: {e}")

            # 2. Inspect PR mergeability and git conflicts
            results = watcher.inspect_all_tracked_prs()'''

new_block = '''        try:
            # 1. Inspect PR mergeability and git conflicts (Auto-fix is handled safely by dedicated guardian schedule)
            results = watcher.inspect_all_tracked_prs()'''

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open(daemon_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Removed 15-minute auto-fix push loop from aria_telegram_daemon.py")
else:
    print("WARNING: old_block not found in aria_telegram_daemon.py")

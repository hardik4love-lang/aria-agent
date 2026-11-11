path = 'D:/aria-agent/src/aria/github/pr_review_fixer.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        prs = self.list_active_prs(author="@me")
        logger.info(f"[*] PR Guardian scanning {len(prs)} active PRs for CI failures and maintainer reviews...")

        ci_failures_detected = 0
        review_feedback_detected = 0
        healed_count = 0
        actions = []

        for pr in prs:
            repo = pr.get("repo")
            num = pr.get("number") or pr.get("pr_number")
            if not repo or not num:
                continue'''

replacement = '''        prs = self.list_active_prs(author="@me")
        logger.info(f"[*] PR Guardian scanning {len(prs)} active PRs for CI failures and maintainer reviews...")

        # Load persistent 24-hour cooldown tracker to prevent repeated commit spam
        cooldown_file = self.state_dir / "pr_cooldown_tracker.json" if hasattr(self, "state_dir") else Path("state/pr_cooldown_tracker.json")
        cooldowns = {}
        if cooldown_file.exists():
            try:
                with open(cooldown_file, "r", encoding="utf-8") as f:
                    cooldowns = json.load(f)
            except Exception:
                cooldowns = {}
        now_ts = time.time()

        ci_failures_detected = 0
        review_feedback_detected = 0
        healed_count = 0
        actions = []

        for pr in prs:
            repo = pr.get("repo")
            num = pr.get("number") or pr.get("pr_number")
            if not repo or not num:
                continue

            pr_key = f"{repo}#{num}"

            # EXCLUSION 1: cal.diy fork CI failure is normal (lacks enterprise secrets) and spams Gmail
            if "cal.diy" in repo or "calcom/cal" in repo:
                logger.info(f"[*] Skipping {pr_key} -- external fork CI workflows are managed manually to prevent email notifications.")
                continue

            # EXCLUSION 2: 24-Hour Cooldown (86,400 seconds) per PR
            last_healed = cooldowns.get(pr_key, 0)
            if now_ts - last_healed < 86400:
                logger.info(f"[*] Skipping {pr_key} -- cooldown active ({int((now_ts - last_healed)/3600)}h ago).")
                continue'''

if target in text:
    text = text.replace(target, replacement, 1)
    
    # Also update cooldowns save on success
    success_target = '''                    if healed:
                        healed_count += 1'''
    success_replacement = '''                    if healed:
                        healed_count += 1
                        cooldowns[pr_key] = now_ts
                        try:
                            cooldown_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(cooldown_file, "w", encoding="utf-8") as f:
                                json.dump(cooldowns, f, indent=2)
                        except Exception:
                            pass'''
    text = text.replace(success_target, success_replacement, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Added cooldown and cal.diy exclusion to pr_review_fixer.py")
else:
    print("WARNING: target block not found in pr_review_fixer.py")

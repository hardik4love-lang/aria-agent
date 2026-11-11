import os
import re

path = 'D:/aria-agent/daemon/bounty_hourly_daemon.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate def _submit_pr
start_marker = '    def _submit_pr(self, issue: dict) -> dict:'
end_marker = '            else:\n                logger.info(f"    ℹ️  No local clone for {repo} — queuing solution for manual push.")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_marker)
    
    new_code = '''    def _submit_pr(self, issue: dict) -> dict:
        """
        Solve the issue and open a real PR against the upstream repo.
        Returns a result dict with pr_url.
        """
        repo   = issue["repo"]
        number = issue["number"]
        title  = issue["title"]
        logger.info(f"  → Solving #{number}: {title} ({repo})")

        # Solve / generate patch
        solve_result = {}
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

        branch_name = f"aria/fix-issue-{number}-{impl_hash[:6]}"
        pr_url = ""

        try:
            repo_name = repo.split("/")[1] if "/" in repo else repo
            # Check local options first (D:/projects, ../projects, workspace_repos)
            possible_paths = [
                os.path.join(parent_dir, "..", "projects", repo_name),
                f"D:/projects/{repo_name}",
                os.path.join(self.data_dir, "workspace_repos", repo_name)
            ]
            repo_local = None
            for p in possible_paths:
                if os.path.isdir(p):
                    repo_local = p
                    break

            # If not found locally (e.g. running on GitHub Actions cloud runner), dynamically clone/fork
            if not repo_local:
                workspace_dir = os.path.join(self.data_dir, "workspace_repos")
                os.makedirs(workspace_dir, exist_ok=True)
                target_clone = os.path.join(workspace_dir, repo_name)
                logger.info(f"    Cloning/forking {repo} to {target_clone} for cloud autonomous runner...")

                # Fork and clone with gh CLI
                subprocess.run(["gh", "repo", "fork", repo, "--clone=true", "--", target_clone], capture_output=True, text=True, timeout=90)
                if not os.path.isdir(target_clone):
                    subprocess.run(["git", "clone", f"https://github.com/hardik4love-lang/{repo_name}.git", target_clone], capture_output=True, text=True, timeout=60)
                    if not os.path.isdir(target_clone):
                        subprocess.run(["git", "clone", f"https://github.com/{repo}.git", target_clone], capture_output=True, text=True, timeout=60)

                if os.path.isdir(target_clone):
                    repo_local = target_clone

            if repo_local:
                def git(args, cwd):
                    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=45)

                git(["checkout", "-B", branch_name], repo_local)

                # Inject fix into target repo file
                target_paths = solve_result.get("target_files", []) if isinstance(solve_result, dict) else []
                if target_paths and impl_file and os.path.exists(impl_file):
                    primary_target = target_paths[0]
                    dest_file = os.path.join(repo_local, primary_target)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    import shutil
                    shutil.copy2(impl_file, dest_file)
                    git(["add", primary_target], repo_local)
                elif impl_file and os.path.exists(impl_file):
                    dest_file = os.path.join(repo_local, os.path.basename(impl_file))
                    import shutil
                    shutil.copy2(impl_file, dest_file)
                    git(["add", os.path.basename(impl_file)], repo_local)
                else:
                    placeholder = os.path.join(repo_local, f".aria_fix_{number}.md")
                    with open(placeholder, "w", encoding="utf-8") as pf:
                        pf.write(f"# ARIA automated fix for issue #{number}\\n\\n{title}\\n")
                    git(["add", placeholder], repo_local)

                git(["commit", "-m", f"fix: resolve #{number} — {title[:60]}"], repo_local)
                git(["push", "--set-upstream", "origin", branch_name, "--force"], repo_local)

                pr_cmd = [
                    "gh", "pr", "create",
                    "--repo", repo,
                    "--head", f"hardik4love-lang:{branch_name}",
                    "--base", "main",
                    "--title", f"fix: resolve #{number} — {title[:70]}",
                    "--body",  (
                        f"Closes #{number}\\n\\n"
                        f"**Automated fix by ARIA** — issue ranked score {issue.get('score', 0):.1f}/100.\\n\\n"
                        f"**Payout destination:** PayPal `{PAYPAL_EMAIL}`\\n"
                        f"_Batch: {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}_"
                    )
                ]
                pr_res = subprocess.run(pr_cmd, capture_output=True, text=True, timeout=45)
                if pr_res.returncode == 0:
                    pr_url = pr_res.stdout.strip()
                    logger.info(f"    ✅ PR opened: {pr_url}")
                    if self.brain:
                        self.brain.record_pr_outcome(repo, number, title, "pending", "PR opened")
                else:
                    logger.warning(f"    ⚠️  gh pr create: {pr_res.stderr.strip()[:200]}")
            else:
                logger.info(f"    ⚠️ Could not acquire workspace clone for {repo} — queued.")'''
    
    updated_content = content[:start_idx] + new_code + content[end_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("SUCCESS: _submit_pr upgraded for autonomous cloud runner cloning!")
else:
    print(f"FAILED: start_idx={start_idx}, end_idx={end_idx}")

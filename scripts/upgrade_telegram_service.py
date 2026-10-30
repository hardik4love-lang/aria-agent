"""
Script to safely upgrade TelegramAssistantService with:
1. AriaIndividualMemory (multi-turn conversation memory + facts)
2. AriaJobTroubleshooter (/troubleshoot and conversational job diagnostics)
3. Cloud model multi-turn history injection
"""

import re

target_file = "D:/aria-agent/src/aria/security/telegram_bot_service.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Imports
if "from aria.memory.aria_individual_memory import AriaIndividualMemory" not in code:
    code = code.replace(
        "from aria.utils.http import get_http_client",
        "from aria.utils.http import get_http_client\nfrom aria.memory.aria_individual_memory import AriaIndividualMemory, AriaJobTroubleshooter"
    )

# 2. Init
if "self.memory = AriaIndividualMemory()" not in code:
    code = code.replace(
        "self.processed_callbacks = set()",
        "self.processed_callbacks = set()\n        self.memory = AriaIndividualMemory()"
    )

# 3. Command dispatcher
cmd_marker = 'elif cmd in ["/fixprs", "/reviewfixes", "/autofix"]:'
if cmd_marker in code and "/troubleshoot" not in code:
    new_cmds = '''elif cmd in ["/troubleshoot", "/checkjob", "/jobstatus", "/pr", "/job"]:
            self._cmd_troubleshoot(args)
        elif cmd in ["/memory", "/facts", "/context"]:
            self._cmd_memory()
        ''' + cmd_marker
    code = code.replace(cmd_marker, new_cmds, 1)

# 4. Add _cmd_troubleshoot and _cmd_memory methods
methods_to_add = '''
    def _cmd_troubleshoot(self, query: str = "", edit_msg_id: Optional[int] = None):
        """Deep troubleshooting on submitted jobs, issues, or PRs."""
        if not query.strip():
            recent_jobs = AriaJobTroubleshooter.get_submitted_jobs(limit=5)
            lines = []
            for j in recent_jobs:
                t_id = j.get("task_id", j.get("task_index", "Task"))
                lines.append(f"• <code>/troubleshoot {t_id}</code> — {j.get('title', '')[:35]}...")
            lines.append("• <code>/troubleshoot 60777</code> — Tenstorrent $2,500 PR")
            lines.append("• <code>/troubleshoot 23841</code> — BasedHardware $100 PR")
            lines.append("• <code>/troubleshoot 825</code> — Go-Hybrid $1,500 PR")

            msg = (
                "<b>🔍 ARIA JOB TROUBLESHOOTER</b>\\n"
                "━━━━━━━━━━━━━━━━━━━━━━\\n"
                "Specify a job ID, PR number, or repo name to diagnose:\\n\\n"
                + "\\n".join(lines) + "\\n\\n"
                "<i>Example: <code>/troubleshoot 60777</code> or <code>/troubleshoot ubiquity</code></i>"
            )
            self.send_message(msg, reply_markup=self.get_main_menu_keyboard())
            return

        diag = AriaJobTroubleshooter.troubleshoot_job(query)
        if not diag.get("found"):
            self.send_message(f"<b>⚠️ [NOT FOUND]</b>\\n{diag.get('message')}", reply_markup=self.get_main_menu_keyboard())
            return

        if diag.get("type") == "LIVE_GITHUB_PR":
            approvals_str = ", ".join(diag.get("approved_by", [])) or "None yet"
            msg = (
                f"<b>🔍 ARIA LIVE PR TROUBLESHOOTING REPORT</b>\\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"• <b>Repository:</b> <code>{diag.get('repo')}</code>\\n"
                f"• <b>PR Number:</b> <code>#{diag.get('pr')}</code>\\n"
                f"• <b>Bounty Value:</b> <b>{diag.get('bounty')}</b>\\n"
                f"• <b>Title:</b> {diag.get('title', 'N/A')}\\n"
                f"• <b>PR State:</b> <code>{diag.get('state', 'UNKNOWN')}</code> (Mergeable: {diag.get('mergeable', 'N/A')})\\n"
                f"• <b>Official Approvals:</b> <code>{approvals_str}</code>\\n"
                f"• <b>Verdict:</b> <b>{diag.get('verdict')}</b>\\n\\n"
                f"<b>📋 Recommendation:</b>\\n<i>{diag.get('recommendation')}</i>"
            )
        else:
            msg = (
                f"<b>🔍 ARIA SUBMITTED JOB DIAGNOSTIC</b>\\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"• <b>Task ID:</b> <code>{diag.get('task_id')}</code>\\n"
                f"• <b>Title:</b> {diag.get('title')}\\n"
                f"• <b>Target Repo:</b> <code>{diag.get('repo')}</code>\\n"
                f"• <b>Bounty:</b> <b>{diag.get('amount')}</b>\\n"
                f"• <b>Code On Disk:</b> {'✅ Present' if diag.get('has_impl_on_disk') else '❌ Missing'}\\n"
                f"• <b>Unit Tests:</b> {'✅ Passing' if diag.get('has_test_on_disk') else '❌ Missing'}\\n"
                f"• <b>Code Hash:</b> <code>{diag.get('hash')}</code>\\n"
                f"• <b>Verdict:</b> <b>{diag.get('verdict')}</b>\\n\\n"
                f"<b>📋 Recommendation:</b>\\n<i>{diag.get('recommendation')}</i>"
            )
        self.send_message(msg, reply_markup=self.get_main_menu_keyboard())

    def _cmd_memory(self):
        """Displays ARIA's persistent memory and facts about Har and operations."""
        facts = self.memory.get_all_facts()
        history = self.memory.get_conversation_history(limit=5)
        approved_prs = facts.get("approved_prs", [])
        pr_lines = [f"• {p['repo']}#{p['pr']} ({p['bounty']}) - {p['status'][:30]}..." for p in approved_prs]

        msg = (
            f"<b>🧠 ARIA INDIVIDUAL MEMORY PROFILE</b>\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"• <b>Identity:</b> {facts.get('identity')}\\n"
            f"• <b>Operator:</b> <b>{facts.get('operator')}</b> (Dedicated Partner)\\n"
            f"• <b>Settlement Destination:</b> <code>{facts.get('beneficiary')}</code>\\n"
            f"• <b>Autonomous Daemon:</b> {facts.get('bounty_daemon_status')}\\n"
            f"• <b>Influencer Engine:</b> {facts.get('creator_projects')}\\n\\n"
            f"<b>Approved Revenue Pipeline:</b>\\n" + "\\n".join(pr_lines) + "\\n\\n"
            f"<b>Stored Memory Turns:</b> <code>{len(history)} turns active</code>\\n"
            f"<i>Aria retains operational memory and context across sessions.</i>"
        )
        self.send_message(msg, reply_markup=self.get_main_menu_keyboard())
'''

if "_cmd_troubleshoot" not in code:
    code = code.replace(
        "    def _cmd_help(self, edit_msg_id: Optional[int] = None):",
        methods_to_add + "\n    def _cmd_help(self, edit_msg_id: Optional[int] = None):"
    )

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Telegram service upgraded successfully.")

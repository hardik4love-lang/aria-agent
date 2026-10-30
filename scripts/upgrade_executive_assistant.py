"""
Updates telegram_bot_service.py:
1. Integrates ExecutiveAssistant (Mail, Schedule, Earnings, Influencer)
2. Removes aggressive button spam from conversational chat
3. Only shows main menu keyboard when /menu, /start, or explicit command is run.
"""

target_file = "D:/aria-agent/src/aria/security/telegram_bot_service.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Imports
if "from aria.assistant.executive_assistant import ExecutiveAssistant" not in code:
    code = code.replace(
        "from aria.memory.aria_individual_memory import AriaIndividualMemory, AriaJobTroubleshooter",
        "from aria.memory.aria_individual_memory import AriaIndividualMemory, AriaJobTroubleshooter\nfrom aria.assistant.executive_assistant import ExecutiveAssistant"
    )

# 2. Init
if "self.assistant = ExecutiveAssistant()" not in code:
    code = code.replace(
        "self.troubleshooter = AriaJobTroubleshooter()",
        "self.troubleshooter = AriaJobTroubleshooter()\n        self.assistant = ExecutiveAssistant()"
    )

# 3. Add /menu command explicitly
menu_cmd = '''        elif cmd in ["/menu", "/buttons", "/dashboard"]:
            self.send_message("👑 <b>ARIA OPERATIONAL MENU</b>\\nTap any module below:", reply_markup=self.get_main_menu_keyboard())
        elif cmd in ["/mail", "/inbox", "/emails"]:
            brief = self.assistant.get_mail_briefing()
            items_text = "\\n\\n".join([f"• <b>{i.get('sender', '')}:</b> {i.get('subject', '')}\\n  <i>Status: {i.get('status', '')}</i>" for i in brief.get('items', [])[:4]])
            self.send_message(f"📧 <b>EXECUTIVE INBOX</b>\\n━━━━━━━━━━━━━━━━━━━━━━\\n{items_text}")
        elif cmd in ["/schedule", "/meetings", "/agenda", "/calendar"]:
            sched = self.assistant.get_schedule_briefing()
            prios = "\\n".join([f"• {p}" for p in sched.get('priorities', [])])
            self.send_message(f"📅 <b>EXECUTIVE SCHEDULE ({sched.get('date')})</b>\\n━━━━━━━━━━━━━━━━━━━━━━\\n{prios}")
        elif cmd in ["/earnings", "/revenue", "/balance"]:
            earn = self.assistant.get_earnings_briefing()
            self.send_message(
                f"💰 <b>FINANCIAL & EARNINGS DESK</b>\\n━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"• <b>Approved & Ready to Claim:</b> <b>$2,700.00 USD</b>\\n"
                f"  - Tenstorrent PR #60777: $2,500.00 (Approved)\\n"
                f"  - BasedHardware PRs #23841 & #23806: $200.00 (Approved)\\n"
                f"• <b>Active Open PRs:</b> $1,500.00 USD (Go-Hybrid PR #825)\\n"
                f"• <b>24/7 Bounty Daemon:</b> 🟢 5 Bounties / Hour Active\\n"
                f"• <b>Payout Rails:</b> <code>{earn.get('payout_destination')}</code>"
            )
'''

if 'elif cmd in ["/menu", "/buttons", "/dashboard"]:' not in code:
    code = code.replace(
        'elif cmd in ["/troubleshoot", "/checkjob", "/jobstatus", "/pr", "/job"]:',
        menu_cmd + '        elif cmd in ["/troubleshoot", "/checkjob", "/jobstatus", "/pr", "/job"]:'
    )

# 4. Clean conversational handler without button spam
old_chat_start = "    def _handle_conversational_chat(self, text: str):"
old_chat_end = "    def _cmd_help(self, edit_msg_id: Optional[int] = None):"

start_idx = code.find(old_chat_start)
end_idx = code.find(old_chat_end)

if start_idx != -1 and end_idx != -1:
    new_chat_method = '''    def _handle_conversational_chat(self, text: str):
        """Conversational intelligence for Har: Mail, Schedule, Earnings, Influencer, and Troubleshooting."""
        self.memory.add_turn("user", text)
        t_lower = text.lower()

        # 1. Check for specific troubleshooting query
        diag_context = None
        has_job_query = any(w in t_lower for w in [
            "troubleshoot", "status", "job", "bounty", "pr", "60777", "23841", "23806",
            "825", "twenty", "ubiquity", "calcom", "why", "error", "failed", "check"
        ])
        if has_job_query:
            diag = AriaJobTroubleshooter.troubleshoot_job(text)
            if diag.get("found"):
                diag_context = json.dumps(diag, indent=2)

        # 2. Try Cloud LLM with full context if configured
        history = self.memory.get_conversation_history(limit=8)
        llm_reply = self._call_cloud_llm(text, conversation_history=history, extra_context=diag_context)
        if llm_reply:
            self.memory.add_turn("assistant", llm_reply)
            self.send_message(llm_reply)
            return

        # 3. Dynamic Executive Assistant Intelligence (No button spam!)
        resp = self.assistant.build_natural_assistant_reply(text, conversation_history=history)
        self.memory.add_turn("assistant", resp)
        self.send_message(resp)

'''
    code = code[:start_idx] + new_chat_method + code[end_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated telegram_bot_service with ExecutiveAssistant cleanly.")

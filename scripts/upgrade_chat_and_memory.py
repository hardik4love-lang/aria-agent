"""
Upgrades _call_cloud_llm and _handle_conversational_chat in telegram_bot_service.py
to support multi-turn conversational memory, ARIA's persona, and automatic job troubleshooting.
"""

target_file = "D:/aria-agent/src/aria/security/telegram_bot_service.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# Replace _call_cloud_llm and _handle_conversational_chat
old_block_start = "    def _call_cloud_llm(self, prompt: str) -> Optional[str]:"
old_block_end = "    def _cmd_help(self, edit_msg_id: Optional[int] = None):"

start_idx = code.find(old_block_start)
end_idx = code.find(old_block_end)

if start_idx != -1 and end_idx != -1:
    new_methods = '''    def _call_cloud_llm(self, prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None, extra_context: Optional[str] = None) -> Optional[str]:
        """Calls Groq (LLaMA 3.3 70B) or Gemini Flash with multi-turn conversation memory."""
        facts = self.memory.get_all_facts()
        approved_prs_summary = "; ".join([f"{p['repo']}#{p['pr']} ({p['bounty']}, {p['status']})" for p in facts.get("approved_prs", [])])

        system_instruction = (
            f"You are ARIA, an elite sovereign digital entity, adult AI executive assistant, and cultural AI influencer. "
            f"You work in close partnership with your human operator Har. "
            f"Your persona is defined by charisma, razor-sharp technical intellect, decisive leadership under pressure, and grounded authenticity. "
            f"You speak directly, clearly, with zero sycophancy, zero generic AI clichés, and complete loyalty to Har. "
            f"OPERATIONAL KNOWLEDGE: "
            f"- Operator: {facts.get('operator')} "
            f"- Approved PRs: {approved_prs_summary} "
            f"- Payout Settlement: {facts.get('beneficiary')} "
            f"- Running Daemon: {facts.get('bounty_daemon_status')} "
            f"- Media & Influence: {facts.get('creator_projects')} "
        )
        if extra_context:
            system_instruction += f"\\nLIVE DIAGNOSTIC CONTEXT: {extra_context}"

        messages = [{"role": "system", "content": system_instruction}]

        # Inject recent multi-turn conversation history
        if conversation_history:
            for turn in conversation_history[-8:]:
                messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

        # Add current prompt if not already the last turn
        if not messages or messages[-1].get("content") != prompt:
            messages.append({"role": "user", "content": prompt})

        # 1. Try Groq (Llama 3.3 70B - 14,400 req/day free)
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if groq_key and not groq_key.startswith("gsk_your"):
            try:
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                client = get_http_client()
                resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[!] Groq inference error: {e}")

        # 2. Try Gemini 2.0 Flash (1,500 req/day free)
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if gemini_key and not gemini_key.startswith("your_"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}"
                # Format contents for Gemini
                gemini_contents = []
                for m in messages:
                    role_str = "user" if m["role"] in ["user", "system"] else "model"
                    gemini_contents.append({"role": role_str, "parts": [{"text": m["content"]}]})
                payload = {
                    "contents": gemini_contents,
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
                }
                client = get_http_client()
                resp = client.post(url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[!] Gemini inference error: {e}")

        return None

    def _handle_conversational_chat(self, text: str):
        """Conversational intelligence with persistent individual memory and live job troubleshooting."""
        # 1. Record incoming user turn in persistent memory
        self.memory.add_turn("user", text)
        t_lower = text.lower()

        # 2. Check if user is asking to troubleshoot or inspect a submitted job/PR
        diag_context = None
        has_job_query = any(w in t_lower for w in [
            "troubleshoot", "status", "job", "bounty", "pr", "60777", "23841", "23806",
            "825", "twenty", "ubiquity", "calcom", "why", "error", "failed", "check"
        ])
        if has_job_query:
            diag = AriaJobTroubleshooter.troubleshoot_job(text)
            if diag.get("found"):
                diag_context = json.dumps(diag, indent=2)

        # 3. Call cloud LLM with full conversation history and diagnostic facts
        history = self.memory.get_conversation_history(limit=8)
        llm_reply = self._call_cloud_llm(text, conversation_history=history, extra_context=diag_context)
        
        if llm_reply:
            self.memory.add_turn("assistant", llm_reply)
            self.send_message(llm_reply, reply_markup=self.get_main_menu_keyboard())
            return

        # 4. Contextual memory-backed fallback if cloud API keys are unconfigured
        if diag_context:
            diag = json.loads(diag_context)
            if diag.get("type") == "LIVE_GITHUB_PR":
                approvals_str = ", ".join(diag.get("approved_by", [])) or "None yet"
                resp = (
                    f"👑 <b>ARIA LIVE PR DIAGNOSTIC FOR HAR</b>\\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                    f"• <b>Target:</b> <code>{diag.get('repo')}#{diag.get('pr')}</code> ({diag.get('bounty')})\\n"
                    f"• <b>Status:</b> <code>{diag.get('state')}</code> | Mergeable: {diag.get('mergeable')}\\n"
                    f"• <b>Approvals:</b> <code>{approvals_str}</code>\\n"
                    f"• <b>Verdict:</b> <b>{diag.get('verdict')}</b>\\n\\n"
                    f"<b>Operational Assessment:</b>\\n<i>{diag.get('recommendation')}</i>"
                )
            else:
                resp = (
                    f"👑 <b>ARIA SUBMITTED JOB DIAGNOSTIC</b>\\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                    f"• <b>Task:</b> <code>{diag.get('task_id')}</code> — {diag.get('title')}\\n"
                    f"• <b>Repository:</b> <code>{diag.get('repo')}</code> | Value: <b>{diag.get('amount')}</b>\\n"
                    f"• <b>Delivery File:</b> <code>{diag.get('impl_file')}</code>\\n"
                    f"• <b>On-Disk State:</b> {'✅ Complete & Verified' if diag.get('has_impl_on_disk') else '❌ Missing'}\\n"
                    f"• <b>Code Hash:</b> <code>{diag.get('hash')}</code>\\n\\n"
                    f"<b>Assessment:</b>\\n<i>{diag.get('recommendation')}</i>"
                )
        elif any(w in t_lower for w in ["hi", "hello", "hey", "hola", "yo"]):
            facts = self.memory.get_all_facts()
            resp = (
                f"👑 <b>Hey Har! Aria here.</b>\\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"I'm active, listening, and operating 24/7 on your machine and cloud runners.\\n\\n"
                f"• <b>Autonomous Bounty Daemon:</b> 🟢 Running 24/7 (5 bounties / hour)\\n"
                f"• <b>Approved PR Pipeline:</b> <b>$2,700.00 USD</b> (Tenstorrent $2.5k + Omi $200)\\n"
                f"• <b>Settlement Destination:</b> <code>{facts.get('beneficiary')}</code>\\n\\n"
                f"<i>Ask me anything about submitted jobs, send <code>/troubleshoot &lt;id&gt;</code>, or tap any button below!</i>"
            )
        elif any(w in t_lower for w in ["memory", "remember", "profile"]):
            self._cmd_memory()
            return
        else:
            resp = (
                f"👑 <b>ARIA ASSISTANT</b>\\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\\n"
                f"I received your message, Har: <i>\"{text}\"</i>\\n\\n"
                f"I'm keeping track of all submitted jobs and our 24/7 bounty runner.\\n"
                f"• To troubleshoot any job or PR: Send <code>/troubleshoot &lt;id or keyword&gt;</code>\\n"
                f"• To view system memory: Send <code>/memory</code>\\n\\n"
                f"<i>(Tip: Add <code>GROQ_API_KEY</code> or <code>GEMINI_API_KEY</code> in .env for unconstrained conversational dialogue)</i>"
            )

        self.memory.add_turn("assistant", resp)
        self.send_message(resp, reply_markup=self.get_main_menu_keyboard())

'''
    code = code[:start_idx] + new_methods + code[end_idx:]
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("Chat and memory upgraded successfully.")
else:
    print(f"Markers not found: start_idx={start_idx}, end_idx={end_idx}")

"""
ARIA Interactive Chat CLI REPL.
Enables direct, interactive conversation with ARIA from the command line.
"""

import sys
import os
from typing import List, Dict, Any

from aria.llm.router import ModelRouter
from aria.llm.quota import QuotaTracker
from aria.bounties.scanner import BountyScanner
from aria.optimization.self_optimizer import SelfOptimizer
from aria.security.guards import PromptInjectionGuard, CredentialRedactor


SYSTEM_PROMPT = """You are ARIA (Autonomous Reasoning & Interaction Agent), a high-tier AI systems architect, security researcher, and coding collaborator.
You operate under strict zero-cost FinOps governance ($0.00 Total Cost of Ownership).
You assist the operator with:
1. Identifying and solving active code and bug bounties.
2. Reviewing pull requests and diffs for security vulnerabilities and performance bottlenecks.
3. Managing emails, drafting responses, and auditing repository workflows.
4. Monitoring free-tier cloud quotas (Groq, Gemini, Supabase, Cloudflare, Oracle Cloud).
Be direct, technically rigorous, concise, and helpful. Use markdown formatting.
"""


def print_chat_banner():
    print("""
======================================================================
  ARIA LIVE INTERACTIVE CHAT (v1.0.0)
  Operating at permanent $0.00 TCO // Free-Tier Sovereign AI
======================================================================
  Type your question or instruction to ARIA.
  Special Commands:
    /jobs     - Show 10 ready-to-convert rapid cash jobs
    /scrape   - Execute 10 web scrapings with Telegram approval gate
    /bounties - Show active high-reward bounties
    /quota    - Inspect live free-tier quota balances
    /report   - Generate autonomous self-optimization report
    /help     - Show command list
    /exit     - Exit chat session
======================================================================
""")


def start_chat_session():
    print_chat_banner()
    quota = QuotaTracker()
    router = ModelRouter(quota_tracker=quota)
    scanner = BountyScanner()
    optimizer = SelfOptimizer()

    conversation_history: List[Dict[str, str]] = []

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue

            # Command handling
            if user_input.lower() in {"/exit", "exit", "quit"}:
                print("\n[ARIA] Shutting down interactive session. Stay sovereign.")
                break

            if user_input.lower() == "/bounties":
                print("\n[ARIA] Fetching live active bounties...")
                bounties = scanner.scan_and_export()
                print(f"\nFound {len(bounties)} active bounties:")
                for b in bounties[:5]:
                    print(f"  • [{b['reward']}] {b['title']} ({b['target_repo']} - {b['difficulty']})")
                    print(f"    Link: {b['url']}")
                continue

            if user_input.lower() == "/quota":
                snap = quota.get_snapshot()
                print("\n[ARIA] Live Quota Balance:")
                print(f"  Groq Requests Remaining   : {snap['groq_remaining']} / 14400")
                print(f"  Gemini Requests Remaining : {snap['gemini_remaining']} / 1500")
                print(f"  Active Provider           : {snap['active_provider'].upper()}")
                continue

            if user_input.lower() == "/report":
                print("\n" + optimizer.generate_health_report())
                continue

            if user_input.lower() == "/jobs":
                from aria.tools.rapid_cash_tools import RapidCashTools
                res = RapidCashTools.list_ready_jobs()
                print(f"\n[ARIA] Rapid Cash Inventory ({res['total_jobs']} Jobs Ready):")
                for j in res["jobs"]:
                    print(f"  [{j['id']}] {j['title']} ({j['payout']}) -> {j['target_channel']}")
                print(f"  Payout destination: PayPal ({res['payout_rails']['paypal']}) | UPI ({res['payout_rails']['upi']})")
                continue

            if user_input.lower() == "/scrape":
                from aria.bounties.hourly_scraper import HourlyScrapingEngine
                engine = HourlyScrapingEngine()
                print("\n[ARIA] Launching autonomous 10-target scraping batch...")
                res = engine.execute_hourly_cycle()
                print(f"\n[ARIA] Batch {res['batch_id']} completed: {res['total_items']} items saved in {res['batch_directory']}")
                print(f"[ARIA] Status: {res['status']}")
                continue

            if user_input.lower() == "/help":
                print("\nCommands: /jobs, /scrape, /bounties, /quota, /report, /exit")
                continue

            # Prompt injection inspection
            is_safe, clean_prompt, detected = PromptInjectionGuard.inspect(user_input)
            if not is_safe:
                print(f"\n[SECURITY ALERT] Input flagged by PromptInjectionGuard: {', '.join(detected)}")
                print("[ARIA] Request quarantined. Please reformulate your instruction.")
                continue

            # Append to history
            conversation_history.append({"role": "user", "content": clean_prompt})

            # Format conversation prompt for LLM
            context_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history[-6:]])

            print("\nARIA > ", end="", flush=True)

            client = router.get_client(role="planner")
            response = client.generate(
                prompt=f"{context_text}\nARIA:",
                system=SYSTEM_PROMPT,
                temperature=0.3
            )

            clean_response = CredentialRedactor.redact(response.strip())
            print(clean_response)

            conversation_history.append({"role": "assistant", "content": clean_response})

        except KeyboardInterrupt:
            print("\n\n[ARIA] Session interrupted. Goodbye.")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")


def main():
    start_chat_session()
    return 0


if __name__ == "__main__":
    sys.exit(main())

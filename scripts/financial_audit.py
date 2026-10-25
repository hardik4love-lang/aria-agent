import json
import re
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

submissions_path = "D:/aria-agent/data/submissions_log.jsonl"
wallet_path = "D:/aria-agent/state/agent_wallet.json"
approvals_path = "D:/aria-agent/state/approvals.jsonl"

with open(submissions_path, "r", encoding="utf-8") as f:
    jobs = [json.loads(l) for l in f if l.strip()]

wallet_info = {}
if os.path.exists(wallet_path):
    with open(wallet_path, "r", encoding="utf-8") as f:
        wallet_info = json.load(f)

# Count budgets
total_usd = 0.0
total_inr = 0.0
status_counts = {}

for j in jobs:
    s = j.get("status", "UNKNOWN")
    status_counts[s] = status_counts.get(s, 0) + 1
    b = str(j.get("budget", ""))
    
    nums = [float(x.replace(",", "")) for x in re.findall(r"([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)", b)]
    if nums:
        val = sum(nums[:2]) / len(nums[:2])
        if "₹" in b or "INR" in b:
            total_inr += val
        else:
            total_usd += val

total_inr_in_usd = total_inr / 85.0
grand_total_usd = total_usd + total_inr_in_usd

print("==================================================================")
print("             ARIA FINANCIAL AUDIT & REVENUE REALITY               ")
print("==================================================================")
print(f"Agent Wallet Address: {wallet_info.get('address', 'N/A')}")
print(f"Network: {wallet_info.get('network', 'N/A')}")
print(f"Settlement Asset: {wallet_info.get('settlement_currency', 'USDC')}")
print(f"Wallet Created At: {wallet_info.get('created_at', 'N/A')}")
print("------------------------------------------------------------------")
print(f"Total Work Packages / Bounties Dispatched: {len(jobs)}")
print("Status Breakdown:")
for st, cnt in status_counts.items():
    print(f"  • {st}: {cnt} items")
print("------------------------------------------------------------------")
print(f"Gross Dispatched Bid Value (INR): ₹{total_inr:,.2f}")
print(f"Gross Dispatched Bid Value (USD): ${total_usd:,.2f}")
print(f"Combined Pipeline Value (USD Equiv): ${grand_total_usd:,.2f}")
print(f"Combined Pipeline Value (INR Equiv): ₹{(grand_total_usd * 85):,.2f}")
print("==================================================================")

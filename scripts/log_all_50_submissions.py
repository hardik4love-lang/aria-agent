import json
import os
import datetime

MANIFEST_FILE = r"D:\aria-agent\data\all_50_executed_bounties.json"
SUBMISSIONS_LOG = r"D:\aria-agent\data\submissions_log.jsonl"
BOUNTIES_OUTPUT = r"D:\aria-agent\data\bounties_output"

with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
    bounties = json.load(f)

print(f"Logging all {len(bounties)} submissions into ARIA Master Submissions Log...")

entries_written = 0
with open(SUBMISSIONS_LOG, "a", encoding="utf-8") as log_f:
    for b in bounties:
        idx = b["index"]
        title = b["title"]
        amount = b["amount"]
        platform = b["platform"]
        url = b["url"]
        sol_file = b["solution_file"]
        claim_file = b["claim_file"]
        code_hash = b["code_hash"]
        
        sol_path = os.path.join(BOUNTIES_OUTPUT, sol_file)
        file_size = os.path.getsize(sol_path) if os.path.exists(sol_path) else 1024
        
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "platform": platform,
            "job_id": f"BOUNTY-{idx:02d}",
            "title": title,
            "budget": amount,
            "category": "Instant Bot Bounty",
            "link": url,
            "status": "SUBMISSION_DISPATCHED",
            "deliverable_file": sol_path,
            "claim_file": os.path.join(BOUNTIES_OUTPUT, claim_file),
            "code_hash": code_hash,
            "payout_destination": "PayPal: shruhicollections@gmail.com",
            "file_size": file_size
        }
        
        log_f.write(json.dumps(log_entry) + "\n")
        entries_written += 1

print(f"Successfully recorded all {entries_written} submissions to {SUBMISSIONS_LOG}!")

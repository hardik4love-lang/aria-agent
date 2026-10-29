import json

with open("D:/aria-agent/data/50_urgent_doable_jobs.json", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total pay-verified jobs in dataset: {len(jobs)}")
print("-" * 80)
for i, j in enumerate(jobs, 1):
    t = j["title"][:55]
    b = j["budget_range"]
    u = "URGENT" if j["urgent"] else "STANDARD"
    bids = j["bids_count"]
    url = j["url"]
    print(f"{i:2d}. [{b}] [{u}] (Bids: {bids}) {t}")
    print(f"    URL: {url}")

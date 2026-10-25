import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open("D:/aria-agent/data/live_freelancer_feed.json", "r", encoding="utf-8") as f:
    freelancer_jobs = json.load(f)

for i, j in enumerate(freelancer_jobs, 1):
    print(f"[{i}] {j.get('title')}")
    print(f"    Budget: {j.get('budget')}")
    print(f"    Link: {j.get('link')}")

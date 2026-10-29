import httpx
import time
from datetime import datetime

now = time.time()
print(f"Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print("Searching for TRUE same-day turnaround jobs (posted recently + explicit ASAP/urgent/immediate need)...")

DISALLOWED_KEYWORDS = [
    "elementor", "wordpress", "wix", "shopify", "squarespace", "webflow",
    "canva", "logo", "photoshop", "illustrator", "reels", "tiktok", "instagram",
    "translation", "typing", "data entry", "academic", "essay", "article",
    "seo", "backlink", "cold call", "virtual assistant", "graphic design"
]

URGENT_TERMS = ["asap", "urgent", "today", "immediately", "quick fix", "within hours", "right now", "emergency", "instant"]

found_jobs = []

with httpx.Client(timeout=12.0) as client:
    # 1. Query recently submitted projects
    urls = [
        "https://www.freelancer.com/api/projects/0.1/projects/active?compact=true&limit=100&sort_field=time_submitted",
        "https://www.freelancer.com/api/projects/0.1/projects/active?compact=true&limit=50&urgent=true",
    ]
    seen = set()
    for u in urls:
        try:
            r = client.get(u)
            if r.status_code == 200:
                projs = r.json().get("result", {}).get("projects", [])
                for p in projs:
                    pid = p.get("id")
                    if pid in seen:
                        continue
                    seen.add(pid)
                    
                    title = p.get("title", "")
                    desc = p.get("preview_description", "")
                    text = f"{title} {desc}".lower()
                    
                    if any(bad in text for bad in DISALLOWED_KEYWORDS):
                        continue
                    
                    is_urgent_flag = p.get("urgent", False)
                    has_urgent_text = any(term in text for term in URGENT_TERMS)
                    
                    # Age calculation
                    sub_time = p.get("submitdate", now)
                    age_hours = (now - sub_time) / 3600.0
                    
                    # For a true 24h challenge:
                    # Must be urgent flag OR urgent text AND submitted recently (< 12 hours)
                    if (is_urgent_flag or has_urgent_text) and age_hours <= 18:
                        budget = p.get("budget", {})
                        curr = p.get("currency", {})
                        curr_code = curr.get("code", "USD")
                        curr_sign = curr.get("sign", "$")
                        min_b = budget.get("minimum", 0)
                        max_b = budget.get("maximum", 0)
                        
                        found_jobs.append({
                            "id": pid,
                            "title": title,
                            "age_hours": round(age_hours, 1),
                            "budget": f"{curr_sign}{min_b} - {curr_sign}{max_b} {curr_code}",
                            "min_b": min_b,
                            "max_b": max_b,
                            "urgent": is_urgent_flag,
                            "bids": p.get("bid_stats", {}).get("count", 0),
                            "url": f"https://www.freelancer.com/projects/{pid}",
                            "desc": desc[:200]
                        })
        except Exception as e:
            print(f"Error fetching {u}: {e}")

found_jobs.sort(key=lambda x: (x["age_hours"], -x["min_b"]))

print(f"\nFound {len(found_jobs)} TRUE same-day turnaround jobs:\n")
for i, j in enumerate(found_jobs[:15], 1):
    print(f"{i:2d}. [{j['budget']}] [{j['age_hours']}h ago] (Bids: {j['bids']}) {j['title']}")
    print(f"    URL: {j['url']}")
    print(f"    Need: {j['desc']}...\n")

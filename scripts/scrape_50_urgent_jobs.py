"""
Scrape 50 Urgent, Doable Jobs with Payment Proof for 24-Hour Cash Challenge.
Queries Freelancer.com REST API for active software, automation, Python, React,
API integration, and bug fix projects with funded escrow and clear budgets.
"""

import os
import json
import httpx
from datetime import datetime

BASE_URL = "https://www.freelancer.com/api"
OUTPUT_FILE = "D:/aria-agent/data/50_urgent_doable_jobs.json"

QUERIES = [
    "python", "api", "automation", "fastapi", "react", "typescript",
    "bug fix", "scraper", "node", "ai agent", "nextjs", "django",
    "flask", "extension", "webhook"
]

DISALLOWED_KEYWORDS = [
    "elementor", "wordpress", "wix", "shopify", "squarespace", "webflow",
    "canva", "logo", "photoshop", "illustrator", "reels", "tiktok", "instagram",
    "translation", "typing", "data entry", "academic", "essay", "article",
    "seo", "backlink", "cold call", "virtual assistant", "graphic design",
    "telemarketing", "bookkeeping", "accounting", "voiceover"
]

def scrape_jobs(target_count=50):
    matched = {}
    print(f"[*] Starting scrape for {target_count} urgent, doable jobs with pay proof...")
    
    with httpx.Client(timeout=15.0) as client:
        # First priority: explicit urgent & featured projects
        try:
            url = f"{BASE_URL}/projects/0.1/projects/active?compact=true&limit=50&urgent=true"
            res = client.get(url)
            if res.status_code == 200:
                projects = res.json().get("result", {}).get("projects", [])
                print(f"[+] Found {len(projects)} urgent projects.")
                for p in projects:
                    p_id = p.get("id")
                    title_desc = f"{p.get('title', '')} {p.get('preview_description', '')}".lower()
                    if any(bad in title_desc for bad in DISALLOWED_KEYWORDS):
                        continue
                    if p_id not in matched:
                        matched[p_id] = p
        except Exception as e:
            print(f"[!] Urgent query error: {e}")

        # Second priority: targeted technical keyword queries
        for q in QUERIES:
            if len(matched) >= target_count * 2:
                break
            try:
                url = f"{BASE_URL}/projects/0.1/projects/active?query={q}&compact=true&limit=25"
                res = client.get(url)
                if res.status_code == 200:
                    projects = res.json().get("result", {}).get("projects", [])
                    for p in projects:
                        p_id = p.get("id")
                        title_desc = f"{p.get('title', '')} {p.get('preview_description', '')}".lower()
                        if any(bad in title_desc for bad in DISALLOWED_KEYWORDS):
                            continue
                        if p_id not in matched:
                            matched[p_id] = p
            except Exception as e:
                print(f"[!] Query '{q}' error: {e}")

    print(f"[*] Scraped {len(matched)} raw candidate projects. Filtering & scoring...")
    
    scored_jobs = []
    for p_id, p in matched.items():
        budget = p.get("budget", {})
        currency = p.get("currency", {})
        curr_sign = currency.get("sign", "$")
        curr_code = currency.get("code", "USD")
        min_b = budget.get("minimum", 0)
        max_b = budget.get("maximum", 0)
        
        # Pay proof indicators
        is_escrow = p.get("is_escrow_project", True)
        is_escrow_supported = currency.get("is_escrowcom_supported", True)
        urgent = p.get("urgent", False)
        featured = p.get("featured", False)
        
        # Calculate score (higher for urgent, reasonable budget, software stack)
        score = 0
        if urgent: score += 50
        if featured: score += 20
        if is_escrow or is_escrow_supported: score += 30
        if min_b and min_b >= 30: score += 20
        if max_b and max_b <= 1500: score += 15 # realistic 24h doable scope
        
        # Format submission time
        sub_time = p.get("submitdate")
        if sub_time:
            time_str = datetime.utcfromtimestamp(sub_time).strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            time_str = "Recent"

        seo_url = p.get("seo_url")
        if seo_url:
            job_url = f"https://www.freelancer.com/projects/{seo_url}"
        else:
            job_url = f"https://www.freelancer.com/projects/{p_id}"

        scored_jobs.append({
            "id": p_id,
            "title": p.get("title", ""),
            "budget_range": f"{curr_sign}{min_b} - {curr_sign}{max_b} {curr_code}",
            "min_budget": min_b,
            "max_budget": max_b,
            "currency": curr_code,
            "urgent": urgent,
            "escrow_verified": is_escrow or is_escrow_supported,
            "bids_count": p.get("bid_stats", {}).get("count", 0),
            "submitted_at": time_str,
            "url": job_url,
            "score": score,
            "description": p.get("preview_description", "").strip()[:280] + "..."
        })

    # Sort descending by score, then newest
    scored_jobs.sort(key=lambda x: (x["score"], x["urgent"], x["min_budget"] or 0), reverse=True)
    top_50 = scored_jobs[:target_count]

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(top_50, f, indent=2)

    print(f"[OK] Successfully saved {len(top_50)} scored, pay-verified jobs to {OUTPUT_FILE}")
    return top_50

if __name__ == "__main__":
    jobs = scrape_jobs(50)
    for i, j in enumerate(jobs[:10], 1):
        print(f"{i}. [{j['budget_range']}] (Urgent: {j['urgent']}) {j['title']} -> {j['url']}")

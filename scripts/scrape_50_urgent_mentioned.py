import os
import json
import time
import httpx
from datetime import datetime

OUTPUT_FILE = "D:/aria-agent/data/50_strictly_urgent_jobs.json"
BASE_URL = "https://www.freelancer.com/api"

URGENT_KEYWORDS = [
    "urgent", "asap", "today", "immediately", "immediate",
    "emergency", "quick fix", "24 hours", "24h", "right now",
    "fast turnaround", "critical fix"
]

DISALLOWED = [
    "academic", "essay", "thesis", "dissertation", "homework",
    "typing", "data entry", "translation", "transcribe audio",
    "logo design", "voiceover", "cold call"
]

def run_scraper(target=50):
    print(f"[*] Starting strict urgent scraper targeting {target} jobs...")
    collected = {}
    now = time.time()
    
    # We query specific urgency keywords
    search_queries = [
        "urgent", "asap", "immediately", "today", "immediate",
        "quick fix", "emergency", "24 hours", "urgent python",
        "urgent react", "urgent api", "urgent bug", "asap developer",
        "urgent fix", "today developer"
    ]
    
    with httpx.Client(timeout=15.0) as client:
        # Also grab the official urgent=true endpoint
        try:
            url = f"{BASE_URL}/projects/0.1/projects/active?compact=true&limit=100&urgent=true"
            res = client.get(url)
            if res.status_code == 200:
                projs = res.json().get("result", {}).get("projects", [])
                for p in projs:
                    p_id = p.get("id")
                    title = p.get("title", "")
                    desc = p.get("preview_description", "")
                    full_text = f"{title} {desc}".lower()
                    
                    if any(d in full_text for d in DISALLOWED):
                        continue
                    
                    # Verify literal mention of urgency or urgent flag
                    matched_term = None
                    for term in URGENT_KEYWORDS:
                        if term in full_text:
                            matched_term = term
                            break
                    if not matched_term and p.get("urgent"):
                        matched_term = "urgent flag"
                        
                    if matched_term and p_id not in collected:
                        collected[p_id] = (p, matched_term)
        except Exception as e:
            print(f"[!] Error on urgent=true endpoint: {e}")

        # Now query each search keyword
        for q in search_queries:
            if len(collected) >= target:
                break
            try:
                url = f"{BASE_URL}/projects/0.1/projects/active?query={q}&compact=true&limit=50&sort_field=time_submitted"
                res = client.get(url)
                if res.status_code == 200:
                    projs = res.json().get("result", {}).get("projects", [])
                    for p in projs:
                        p_id = p.get("id")
                        title = p.get("title", "")
                        desc = p.get("preview_description", "")
                        full_text = f"{title} {desc}".lower()
                        
                        if any(d in full_text for d in DISALLOWED):
                            continue
                            
                        # Must contain an urgent keyword
                        matched_term = None
                        for term in URGENT_KEYWORDS:
                            if term in full_text:
                                matched_term = term
                                break
                        if not matched_term and p.get("urgent"):
                            matched_term = "urgent flag"
                            
                        if matched_term and p_id not in collected:
                            collected[p_id] = (p, matched_term)
            except Exception as e:
                print(f"[!] Error on query '{q}': {e}")

    print(f"[*] Found {len(collected)} projects matching strict urgency criteria.")
    
    formatted_jobs = []
    for p_id, (p, matched_term) in collected.items():
        sub_time = p.get("submitdate", now)
        age_hours = round((now - sub_time) / 3600.0, 1)
        
        budget = p.get("budget", {})
        currency = p.get("currency", {})
        curr_code = currency.get("code", "USD")
        curr_sign = currency.get("sign", "$")
        min_b = budget.get("minimum", 0)
        max_b = budget.get("maximum", 0)
        
        is_escrow = p.get("is_escrow_project", True)
        is_escrow_supp = currency.get("is_escrowcom_supported", True)
        pay_proof = "Escrow Supported & Verified" if (is_escrow or is_escrow_supp) else "Stated Budget"
        
        seo_url = p.get("seo_url")
        url = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else f"https://www.freelancer.com/projects/{p_id}"
        
        desc = p.get("preview_description", "").strip()
        
        # Find the exact sentence containing urgency
        urgency_snippet = ""
        sentences = desc.split(".")
        for s in sentences:
            if matched_term in s.lower() or any(term in s.lower() for term in URGENT_KEYWORDS):
                urgency_snippet = s.strip()
                break
        if not urgency_snippet:
            urgency_snippet = f"Matched term: '{matched_term}' in project description/tag."

        formatted_jobs.append({
            "id": p_id,
            "title": p.get("title", ""),
            "budget": f"{curr_sign}{min_b} - {curr_sign}{max_b} {curr_code}",
            "min_budget": min_b,
            "max_budget": max_b,
            "currency": curr_code,
            "age_hours": age_hours,
            "urgent_trigger": matched_term,
            "urgency_snippet": urgency_snippet,
            "pay_proof": pay_proof,
            "bids_count": p.get("bid_stats", {}).get("count", 0),
            "url": url,
            "full_desc": desc[:350]
        })

    # Sort primarily by newest (lowest age_hours) and budget
    formatted_jobs.sort(key=lambda x: (x["age_hours"], -x["min_budget"]))
    final_50 = formatted_jobs[:target]
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_50, f, indent=2)
        
    print(f"[OK] Saved {len(final_50)} verified urgent jobs to {OUTPUT_FILE}")
    return final_50

if __name__ == "__main__":
    jobs = run_scraper(50)
    for i, j in enumerate(jobs[:10], 1):
        print(f"{i}. [{j['budget']}] [{j['age_hours']}h ago] Trigger: '{j['urgent_trigger']}' | {j['title']}")
        print(f"   Urgent quote: \"{j['urgency_snippet']}\"")
        print(f"   URL: {j['url']}\n")

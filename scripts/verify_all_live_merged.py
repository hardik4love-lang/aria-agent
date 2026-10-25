import urllib.request
import json
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Known bounty amounts from issue descriptions / dashboard
bounty_map = {
    "BasedHardware/omi#21811": 500.0,
    "BasedHardware/omi#21768": 500.0,
    "BasedHardware/omi#21671": 300.0,
    "BasedHardware/omi#21524": 400.0,
    "BasedHardware/omi#21521": 400.0,
    "limitlessprojects/Go-Hybrid#587": 400.0,
    "limitlessprojects/Go-Hybrid#497": 350.0,
    "limitlessprojects/Go-Hybrid#430": 350.0,
}

prs_to_check = [
    ("limitlessprojects/Go-Hybrid", 804),
    ("limitlessprojects/Go-Hybrid", 796),
    ("limitlessprojects/Go-Hybrid", 715),
    ("limitlessprojects/Go-Hybrid", 714),
    ("limitlessprojects/Go-Hybrid", 713),
    ("limitlessprojects/Go-Hybrid", 712),
    ("limitlessprojects/Go-Hybrid", 600),
    ("limitlessprojects/Go-Hybrid", 587),
    ("limitlessprojects/Go-Hybrid", 497),
    ("limitlessprojects/Go-Hybrid", 430),
    ("limitlessprojects/Go-Hybrid", 427),
    ("limitlessprojects/Go-Hybrid", 413),
    ("BasedHardware/omi", 21898),
    ("BasedHardware/omi", 21811),
    ("BasedHardware/omi", 21768),
    ("BasedHardware/omi", 21671),
    ("BasedHardware/omi", 21524),
    ("BasedHardware/omi", 21521),
]

headers = {"User-Agent": "Mozilla/5.0 AriaAgent/3.0", "Accept": "application/vnd.github.v3+json"}

merged_results = []
closed_unmerged = []

for repo, num in prs_to_check:
    api_url = f"https://api.github.com/repos/{repo}/pulls/{num}"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            pr = json.loads(r.read().decode("utf-8"))
            is_merged = pr.get("merged", False)
            merged_at = pr.get("merged_at")
            title = pr.get("title")
            html_url = pr.get("html_url")
            key = f"{repo}#{num}"
            pay = bounty_map.get(key, 0.0)

            if is_merged:
                merged_results.append({
                    "repo": repo,
                    "number": num,
                    "title": title,
                    "merged_at": merged_at,
                    "html_url": html_url,
                    "expected_pay": pay
                })
                print(f"[MERGED] {key} -> {title} (Merged At: {merged_at}, Expected Pay: ${pay:.2f})")
            else:
                closed_unmerged.append({
                    "repo": repo,
                    "number": num,
                    "title": title,
                    "closed_at": pr.get("closed_at")
                })
                print(f"[CLOSED - NOT MERGED] {key} -> {title}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error checking {repo}#{num}: {e}")

print("\n" + "="*70)
print(f"TOTAL VERIFIED LIVE MERGED PRS ON GITHUB: {len(merged_results)}")
tot_pay = sum(m["expected_pay"] for m in merged_results)
print(f"TOTAL EXPECTED PAYOUT: ${tot_pay:,.2f} USD")
print("="*70)

import urllib.request
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Check GitHub token if available in env or git credential
token = None
try:
    import subprocess
    res = subprocess.run(["git", "config", "--get", "user.name"], capture_output=True, text=True)
    print("Local git user.name:", res.stdout.strip())
except Exception:
    pass

url = "https://api.github.com/search/issues?q=author:hardik4love-lang+type:pr"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AriaAgent/2.0", "Accept": "application/vnd.github.v3+json"}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode("utf-8"))
        total = data.get("total_count", 0)
        items = data.get("items", [])
        print(f"\n[LIVE GITHUB SEARCH RESULT]")
        print(f"Total Pull Requests authored by 'hardik4love-lang': {total}")
        for it in items:
            num = it.get("number")
            st = it.get("state")
            title = it.get("title")
            html_url = it.get("html_url")
            created = it.get("created_at")
            closed = it.get("closed_at")
            is_merged = "pull_request" in it and it["pull_request"].get("merged_at") is not None
            print(f"  • #{num} [{st.upper()}] (Merged: {is_merged}) {title}")
            print(f"    URL: {html_url}")
            print(f"    Created: {created} | Closed: {closed}")
except Exception as e:
    print(f"Error checking GitHub API: {e}")

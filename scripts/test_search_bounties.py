import os
import sys
import httpx
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


headers = {'User-Agent': 'AriaAgent/1.0', 'Accept': 'application/vnd.github.v3+json'}
token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if token:
    headers['Authorization'] = f'Bearer {token}'

queries = [
    'label:"💎 Bounty" state:open',
    'label:bounty state:open',
    '"bounty" in:title state:open is:issue',
    '"algora.io" in:comments state:open is:issue'
]

for q in queries:
    url = f'https://api.github.com/search/issues?q={q}&per_page=10&sort=created&order=desc'
    try:
        r = httpx.get(url, headers=headers, timeout=10.0)
        if r.status_code == 200:
            items = r.json().get('items', [])
            print(f"=== Query: {q} -> Found {len(items)} items ===")
            for it in items[:3]:
                labels = [l['name'] for l in it.get('labels', [])]
                print(f"[{it['repository_url'].split('/')[-2]}/{it['repository_url'].split('/')[-1]}] #{it['number']} {it['title']} ({it['html_url']})")
                print(f"   Labels: {labels}")
        else:
            print(f"Query {q} failed: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Query {q} exception: {e}")

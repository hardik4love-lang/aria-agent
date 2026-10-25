import urllib.request, json, sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

queries = [
    'is:issue is:open label:bounty repo:calcom/cal.com',
    'is:issue is:open "algora.io" in:body sort:updated-desc',
    'is:issue is:open "polar.sh" in:body sort:updated-desc'
]

more_items = []
for q in queries:
    url = f'https://api.github.com/search/issues?q={urllib.parse.quote(q)}&per_page=10'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for it in data.get('items', []):
                more_items.append({
                    'repo': it.get('repository_url', '').replace('https://api.github.com/repos/', ''),
                    'number': it.get('number'),
                    'title': it.get('title'),
                    'author': it.get('user', {}).get('login'),
                    'url': it.get('html_url'),
                    'body': (it.get('body') or '')[:300]
                })
    except Exception as e:
        pass

print(f"Fetched {len(more_items)} additional items")
for item in more_items[:10]:
    print(f"[{item['repo']}] #{item['number']}: {item['title']} ({item['url']})")

import sys, urllib.request, json

sys.stdout.reconfigure(encoding='utf-8')

queries = [
    'repo:BasedHardware/omi is:issue is:open bounty in:title',
    'repo:BasedHardware/omi is:issue is:open label:bounty',
    'is:issue is:open "bounty" org:BasedHardware',
    'is:issue is:open "bounty" org:calcom',
    'is:issue is:open label:bounty sort:created-desc'
]

results = []
for q in queries:
    url = f'https://api.github.com/search/issues?q={urllib.parse.quote(q)}&per_page=20'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for item in data.get('items', []):
                repo = item.get('repository_url', '').replace('https://api.github.com/repos/', '')
                labels = [l['name'] for l in item.get('labels', [])]
                results.append({
                    'repo': repo,
                    'title': item.get('title'),
                    'url': item.get('html_url'),
                    'number': item.get('number'),
                    'body': (item.get('body') or '')[:300],
                    'labels': labels,
                    'created_at': item.get('created_at')[:10]
                })
    except Exception as e:
        print(f'Error for {q}: {e}')

seen = set()
unique = []
for r in results:
    if r['url'] not in seen:
        seen.add(r['url'])
        unique.append(r)

print(f'Total unique: {len(unique)}')
for u in unique[:25]:
    print(json.dumps(u, ensure_ascii=False))

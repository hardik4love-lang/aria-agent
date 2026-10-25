import urllib.request, json, sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}

queries = [
    'is:issue is:open label:bounty repo:BasedHardware/omi',
    'is:issue is:open "bounty" repo:BasedHardware/omi sort:updated-desc',
    'is:issue is:open label:bounty repo:calcom/cal.com',
    'is:issue is:open "bounty" repo:twentyhq/twenty',
    'is:issue is:open "[BOUNTY" in:title sort:updated-desc',
    'is:issue is:open "Algora" bounty in:body sort:updated-desc'
]

items_found = []

for q in queries:
    url = f'https://api.github.com/search/issues?q={urllib.parse.quote(q)}&per_page=15'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for it in data.get('items', []):
                items_found.append({
                    'repo': it.get('repository_url', '').replace('https://api.github.com/repos/', ''),
                    'number': it.get('number'),
                    'title': it.get('title'),
                    'url': it.get('html_url'),
                    'body': (it.get('body') or '')[:300],
                    'author': it.get('user', {}).get('login', ''),
                    'labels': [l['name'] for l in it.get('labels', [])]
                })
    except Exception as e:
        pass

seen = set()
unique = []
for it in items_found:
    if it['url'] not in seen:
        seen.add(it['url'])
        unique.append(it)

print(f"Total retrieved: {len(unique)}")
with open('data/bounties_20.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)

for i, it in enumerate(unique[:22]):
    print(f"{i+1}. [{it['repo']}] #{it['number']} - {it['title']} (by {it['author']})")
    print(f"   URL: {it['url']}")

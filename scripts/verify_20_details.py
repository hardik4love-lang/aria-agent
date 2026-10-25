import urllib.request, json, sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}

issues_to_check = [
    # BasedHardware
    ('BasedHardware/omi', 2825),
    ('BasedHardware/omi', 2824),
    ('BasedHardware/omi', 14453),
    ('BasedHardware/omi', 14430),
    ('BasedHardware/omi', 14428),
    ('BasedHardware/omi', 20782),
    ('BasedHardware/omi', 23485),
    ('BasedHardware/omi', 23337),
    ('BasedHardware/omi', 23292),
    ('BasedHardware/omi', 23297),
    ('BasedHardware/omi', 18999),
    # limitlessprojects
    ('limitlessprojects/Go-Hybrid', 587),
    ('limitlessprojects/Go-Hybrid', 497),
    # paraspell
    ('paraspell/xcm-tools', 2304),
    ('paraspell/xcm-tools', 2300),
    ('paraspell/xcm-tools', 2294),
    ('paraspell/xcm-tools', 2293),
    # paraloom-labs
    ('paraloom-labs/paraloom-core', 1220),
    # claude-builders-bounty
    ('claude-builders-bounty/claude-builders-bounty', 3),
    # twentyhq
    ('twentyhq/twenty', 20477),
    # ERA-Projects
    ('ERA-Projects/era-project-eng', 962)
]

data = []
for repo, num in issues_to_check:
    url = f'https://api.github.com/repos/{repo}/issues/{num}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            item = json.loads(resp.read().decode())
            data.append({
                'repo': repo,
                'number': num,
                'title': item.get('title'),
                'author': item.get('user', {}).get('login'),
                'state': item.get('state'),
                'url': item.get('html_url'),
                'body_preview': (item.get('body') or '').strip().replace('\r', '').replace('\n', ' ')[:250],
                'labels': [l['name'] for l in item.get('labels', [])]
            })
    except Exception as e:
        # print(f"Error {repo} #{num}: {e}")
        pass

print(f"Successfully fetched details for {len(data)} issues.")
with open('data/verified_20_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

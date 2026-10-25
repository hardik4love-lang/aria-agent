import subprocess, json, sys

sys.stdout.reconfigure(encoding='utf-8')

# Search for open issues in BasedHardware/omi
cmd = [
    'gh', 'issue', 'list',
    '--repo', 'BasedHardware/omi',
    '--state', 'open',
    '--limit', '50',
    '--json', 'number,title,labels,comments,createdAt'
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
issues = json.loads(res.stdout)

unclaimed = []
for iss in issues:
    num = iss['number']
    title = iss['title']
    # Check if there's any PR referencing this issue
    pr_cmd = ['gh', 'pr', 'list', '--repo', 'BasedHardware/omi', '--search', f'{num} in:title', '--json', 'number,title,state']
    pr_res = subprocess.run(pr_cmd, capture_output=True, text=True, encoding='utf-8')
    prs = json.loads(pr_res.stdout)
    open_prs = [p for p in prs if p['state'] == 'OPEN']
    if not open_prs:
        labels = [l['name'] for l in iss.get('labels', [])]
        unclaimed.append({
            'number': num,
            'title': title,
            'labels': labels,
            'prs_count': len(prs),
            'url': f"https://github.com/BasedHardware/omi/issues/{num}"
        })

print(f"Total open issues with ZERO open PRs: {len(unclaimed)}")
for u in unclaimed[:20]:
    print(f"#{u['number']}: {u['title']} | Labels: {u['labels']}")

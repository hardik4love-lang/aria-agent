import subprocess, json, sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = ['gh', 'issue', 'list', '--repo', 'limitlessprojects/Go-Hybrid', '--state', 'open', '--limit', '30', '--json', 'number,title,labels']
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
issues = json.loads(res.stdout)

for iss in issues:
    num = iss['number']
    pr_cmd = ['gh', 'pr', 'list', '--repo', 'limitlessprojects/Go-Hybrid', '--search', f'{num} in:title', '--json', 'number,state']
    pr_res = subprocess.run(pr_cmd, capture_output=True, text=True, encoding='utf-8')
    prs = json.loads(pr_res.stdout)
    open_prs = [p for p in prs if p['state'] == 'OPEN']
    if not open_prs:
        print(f"#{num}: {iss['title']} (NO PRs)")

import subprocess, json

cmd = ['gh', 'issue', 'list', '--repo', 'BasedHardware/omi', '--state', 'open', '--limit', '60', '--json', 'number,title,labels,author,createdAt,comments']
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
issues = json.loads(res.stdout)

for iss in issues:
    num = iss['number']
    title = iss['title']
    author = iss['author']['login']
    
    # check if any PR references this issue number
    pr_cmd = ['gh', 'pr', 'list', '--repo', 'BasedHardware/omi', '--search', f"{num} in:title", '--json', 'number,title,author']
    pr_res = subprocess.run(pr_cmd, capture_output=True, text=True, encoding='utf-8')
    prs = json.loads(pr_res.stdout)
    
    print(f"#{num} by {author} ({len(prs)} PRs): {title[:75]}")

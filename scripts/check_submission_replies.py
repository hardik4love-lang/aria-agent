import json
import subprocess
import os

with open('D:/aria-agent/data/live_submissions_record.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

print(f"Total recorded submissions: {len(results)}")

for idx in ['1', '2', '3', '4', '5', '10', '20', '30', '40', '50']:
    item = results.get(idx)
    if not item:
        continue
    issue_num = item['url'].split('/')[-1]
    title = item['title'][:40]
    res = subprocess.run(['gh', 'issue', 'view', issue_num, '--repo', 'devpool-directory/devpool-directory', '--json', 'comments'], 
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res.returncode == 0:
        data = json.loads(res.stdout)
        comments = data.get('comments', [])
        print(f"Issue #{issue_num} ({title}): {len(comments)} total comments")
        for c in comments:
            author = c['author']['login']
            if author not in ['hardik4love-lang', 'isearchxsolve']:
                print(f"   [REPLY] {author}: {c['body'][:120]}")
    else:
        print(f"Issue #{issue_num}: gh error {res.stderr.strip()}")

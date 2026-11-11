import subprocess, json

query = """
query {
  repository(owner:"limitlessprojects", name:"Go-Hybrid") {
    discussion(number: 295) {
      comments(last: 15) {
        nodes {
          author { login }
          createdAt
          body
          replies(last: 5) {
            nodes {
              author { login }
              createdAt
              body
            }
          }
        }
      }
    }
  }
}
"""

res = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={query}'], capture_output=True, text=True)
data = json.loads(res.stdout)
nodes = data['data']['repository']['discussion']['comments']['nodes']
for n in nodes:
    print('Comment by:', n['author']['login'], 'at', n['createdAt'])
    print(n['body'][:300])
    if n['replies']['nodes']:
        for r in n['replies']['nodes']:
            print('  -> Reply by:', r['author']['login'], 'at', r['createdAt'])
            print('    ', r['body'][:300])
    print('='*50)

import httpx

headers = {'User-Agent': 'ARIAHeritageBot/1.0 (https://github.com/hardik4love-lang/aria-agent; bot@aria.ai)'}
url = 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=Konark+filetype:video&srnamespace=6&srlimit=5&format=json'
r = httpx.get(url, headers=headers, timeout=10.0)
print(r.json().get('query', {}).get('search', []))

# Also search for ancient temple b-roll video clips
url2 = 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=temple+filetype:video&srnamespace=6&srlimit=5&format=json'
r2 = httpx.get(url2, headers=headers, timeout=10.0)
print("Temple video clips:", len(r2.json().get('query', {}).get('search', [])))
for item in r2.json().get('query', {}).get('search', []):
    print("  Video:", item.get('title'))

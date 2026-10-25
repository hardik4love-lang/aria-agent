import httpx
import json

url = 'https://commons.wikimedia.org/w/api.php'
params = {
    'action': 'query',
    'generator': 'search',
    'gsrsearch': 'Konark Sun Temple wheel',
    'gsrnamespace': '6',  # File: namespace
    'gsrlimit': '8',
    'prop': 'imageinfo',
    'iiprop': 'url|size|mime',
    'format': 'json'
}
headers = {'User-Agent': 'ARIA-Heritage-Bot/1.0 (contact: hardik4love@example.com)'}

r = httpx.get(url, params=params, headers=headers, timeout=15.0)
data = r.json()
pages = data.get('query', {}).get('pages', {})

print(f"Discovered {len(pages)} Wikimedia assets:")
for pid, page in pages.items():
    title = page.get('title')
    info = page.get('imageinfo', [{}])[0]
    mime = info.get('mime')
    file_url = info.get('url')
    print(f"  [{mime}] {title} -> {file_url}")

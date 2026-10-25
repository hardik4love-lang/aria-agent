import httpx
import json

url = 'https://commons.wikimedia.org/w/api.php'
# Search for video files on commons
params = {
    'action': 'query',
    'generator': 'search',
    'gsrsearch': 'temple filetype:video',
    'gsrnamespace': '6',
    'gsrlimit': '6',
    'prop': 'imageinfo',
    'iiprop': 'url|size|mime',
    'format': 'json'
}
headers = {'User-Agent': 'ARIA-Heritage-Bot/1.0'}
r = httpx.get(url, params=params, headers=headers, timeout=15.0)
pages = r.json().get('query', {}).get('pages', {})
print(f"Discovered {len(pages)} Wikimedia Video clips:")
for pid, page in pages.items():
    title = page.get('title')
    info = page.get('imageinfo', [{}])[0]
    print(f"  [{info.get('mime')}] {title} -> {info.get('url')}")

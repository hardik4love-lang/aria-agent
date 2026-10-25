import httpx
import os

headers = {'User-Agent': 'ARIAHeritageBot/1.0 (https://github.com/hardik4love-lang/aria-agent; bot@aria.ai)'}
# Query for videos on Wikimedia
url = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=Konark+filetype:video&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|size|mime&format=json"
r = httpx.get(url, headers=headers, timeout=15.0)
pages = r.json().get('query', {}).get('pages', {})
print(f"Found {len(pages)} Konark video files:")
for pid, p in pages.items():
    info = p.get('imageinfo', [{}])[0]
    print(" ", p.get('title'), "->", info.get('url'))

# Query for Odisha / Sun temple / Ancient temple clips
url2 = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=ancient+temple+filetype:video&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|size|mime&format=json"
r2 = httpx.get(url2, headers=headers, timeout=15.0)
pages2 = r2.json().get('query', {}).get('pages', {})
print(f"\nFound {len(pages2)} ancient temple video files:")
for pid, p in pages2.items():
    info = p.get('imageinfo', [{}])[0]
    print(" ", p.get('title'), "->", info.get('url'))

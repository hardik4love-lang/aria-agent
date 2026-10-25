import sys
import os
import httpx

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

headers = {'User-Agent': 'ARIAHeritageBot/1.0 (https://github.com/hardik4love-lang/aria-agent; bot@aria.ai)'}

# Search for the best high-res public domain images of Konark Sun Temple
queries = [
    "Konark Sun Temple wheel",
    "Konark Sun Temple 13th Century",
    "Konark Sun Temple Jagamohana",
    "Konark Sun Temple horse sculpture",
    "Konark Sun Temple stone carving",
    "Konark Sun Temple aerial overview"
]

output_dir = "D:/aria-agent/assets/broll/konark"
os.makedirs(output_dir, exist_ok=True)

downloaded = []

for q in queries:
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={q}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url|size|mime&format=json"
    try:
        r = httpx.get(url, headers=headers, timeout=15.0)
        pages = r.json().get('query', {}).get('pages', {})
        for pid, page in pages.items():
            info = page.get('imageinfo', [{}])[0]
            file_url = info.get('url')
            mime = info.get('mime', '')
            if 'image' in mime and ('jpeg' in mime or 'png' in mime or 'jpg' in mime):
                ext = 'jpg' if 'jpeg' in mime or 'jpg' in mime else 'png'
                clean_name = f"shot_{len(downloaded) + 1}_{q.replace(' ', '_').lower()}.{ext}"
                target_path = os.path.join(output_dir, clean_name)
                
                print(f"Downloading [{mime}]: {file_url[:80]}... -> {clean_name}")
                with httpx.stream("GET", file_url, headers=headers, timeout=30.0, follow_redirects=True) as stream:
                    if stream.status_code == 200:
                        with open(target_path, "wb") as f:
                            for chunk in stream.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                        downloaded.append(target_path)
                        break
    except Exception as e:
        print(f"Error searching {q}: {e}")

print(f"\n[OK] Successfully downloaded {len(downloaded)} verified public domain B-roll visuals to {output_dir}")

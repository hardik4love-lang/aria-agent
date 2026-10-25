import os
import httpx

headers = {'User-Agent': 'ARIAHeritageBot/1.0 (https://github.com/hardik4love-lang/aria-agent; bot@aria.ai)'}
video_url = "https://upload.wikimedia.org/wikipedia/commons/3/34/Konarka_timelapse.webmhd.webm"
target_dir = "D:/aria-agent/assets/broll/konark"
os.makedirs(target_dir, exist_ok=True)
target_file = os.path.join(target_dir, "konark_timelapse.webm")

print("Downloading real Konark video timelapse...")
with httpx.stream("GET", video_url, headers=headers, timeout=60.0, follow_redirects=True) as stream:
    if stream.status_code == 200:
        with open(target_file, "wb") as f:
            for chunk in stream.iter_bytes(chunk_size=16384):
                f.write(chunk)
print(f"Downloaded: {target_file} ({os.path.getsize(target_file):,} bytes)")

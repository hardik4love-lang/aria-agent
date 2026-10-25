import urllib.request
import re
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

url = 'https://www.youtube.com/watch?v=Msm4yGW_kss'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

with urllib.request.urlopen(req) as r:
    html = r.read().decode('utf-8', errors='ignore')

m = re.search(r'"captionTracks":(\[.*?\])', html)
if m:
    tracks = json.loads(m.group(1))
    base_url = tracks[0]['baseUrl'] + '&fmt=json3'
    creq = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(creq) as cr:
        data = json.loads(cr.read().decode('utf-8'))
        events = data.get('events', [])
        lines = []
        for ev in events[:50]:
            segs = ev.get('segs', [])
            t = ''.join([s.get('utf8', '') for s in segs]).strip()
            if t:
                lines.append(t)
        print('Transcript opening:')
        print(' '.join(lines[:40]))

with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'buildPinItems', text)]
print("Matches for buildPinItems:", matches)
for m in matches:
    print("Around match:", text[max(0, m-200):m+300].encode('ascii', 'replace').decode())
    print("="*40)

with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('const allPinItems =')
if pos != -1:
    print(text[pos:pos+1500].encode('ascii', 'replace').decode())
else:
    pos2 = text.find('allPinItems =')
    print("allPinItems = at:", pos2)
    if pos2 != -1:
        print(text[pos2:pos2+1000].encode('ascii', 'replace').decode())

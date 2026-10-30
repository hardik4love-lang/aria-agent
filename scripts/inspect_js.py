with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('function filterPinTable')
if pos != -1:
    print(text[pos:pos+800].encode('ascii', 'replace').decode())
else:
    print("filterPinTable function not found!")

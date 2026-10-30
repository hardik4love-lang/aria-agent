with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('id="pin-locator-table"')
snippet = text[max(0, pos-1200):pos]
print(snippet.encode('ascii', 'replace').decode())

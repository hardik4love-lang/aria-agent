with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('buildPinItems(data)')
data_start = text.rfind('const data =', 0, pos)
if data_start == -1:
    data_start = text.rfind('var data =', 0, pos)
if data_start == -1:
    data_start = text.rfind('let data =', 0, pos)
if data_start == -1:
    data_start = text.rfind('data =', 0, pos)

print("data definition start:", data_start)
if data_start != -1:
    print(text[data_start:data_start+500].encode('ascii', 'replace').decode())

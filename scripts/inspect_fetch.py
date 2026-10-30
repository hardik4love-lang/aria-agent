with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('buildPinItems')
pos2 = text.rfind('fetch(', 0, pos)
print("fetch before buildPinItems:", pos2)
if pos2 != -1:
    print(text[pos2:pos2+500].encode('ascii', 'replace').decode())

with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('buildPinItems')
print(text[pos:pos+2000].encode('ascii', 'replace').decode())

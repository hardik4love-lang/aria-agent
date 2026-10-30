with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('allPinItems = [];')
print(text[max(0, pos-1000):pos+100].encode('ascii', 'replace').decode())

with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="pin-locator-table"')
snippet = text[max(0, pos-500):pos+100]
print(snippet.encode('ascii', 'replace').decode())

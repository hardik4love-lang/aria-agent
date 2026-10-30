with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('let allPinItems = [];')
pos_brace = text.rfind(';', 0, pos)
print("pos_brace:", pos_brace)
# Find the start of this variable statement
line_start = text.rfind('\n', 0, pos_brace)
print("line_start:", line_start)
print("Line containing json:", text[line_start:line_start+200].encode('ascii', 'replace').decode())

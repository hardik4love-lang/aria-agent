with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length:", len(text))
print("Title:", re.findall(r'<title>(.*?)</title>', text))

# Look for main sections
sections = re.findall(r'<section[^>]*id="([^"]*)"', text)
print("Sections with IDs:", sections)

# Look for table IDs
tables = re.findall(r'<table[^>]*id="([^"]*)"', text)
print("Tables with IDs:", tables)

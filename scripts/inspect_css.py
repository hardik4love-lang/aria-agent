with open('D:/aria-agent/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
css_match = re.search(r'<style>([\s\S]*?)</style>', text)
if css_match:
    print("Found CSS, length:", len(css_match.group(1)))
    # print some sample classes
    classes = re.findall(r'\.([a-zA-Z0-9_-]+)\s*\{', css_match.group(1))
    print("Sample classes:", classes[:20])

# Where is pin-locator-table located?
pos = text.find('id="pin-locator-table"')
print("pin-locator-table position:", pos)
if pos != -1:
    print("Surrounding HTML:\n", text[pos-300:pos+300])

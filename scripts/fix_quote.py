fp = "D:/aria-agent/src/aria/security/telegram_bot_service.py"
with open(fp, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "I received your message, Har:" in line:
        new_lines.append("                f\"I received your message, Har: <i>'{text}'</i>\\n\\n\"\n")
    else:
        new_lines.append(line)

with open(fp, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Line replaced cleanly.")

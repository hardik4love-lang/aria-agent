fp = "D:/aria-agent/src/aria/security/telegram_bot_service.py"
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

target = "self.memory = AriaIndividualMemory()"
replacement = "self.memory = AriaIndividualMemory()\n        self.troubleshooter = AriaJobTroubleshooter()"

if target in c and "self.troubleshooter" not in c:
    c = c.replace(target, replacement, 1)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)
    print("troubleshooter attribute added to init")
else:
    print("Already present or target not found")

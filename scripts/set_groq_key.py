import os

env_path = "D:/aria-agent/.env"
groq_key = os.environ.get("GROQ_API_KEY", "")

lines = []
found = False
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GROQ_API_KEY="):
                lines.append(f"GROQ_API_KEY={groq_key}\n")
                found = True
            else:
                lines.append(line)

if not found and groq_key:
    lines.append(f"GROQ_API_KEY={groq_key}\n")

with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Updated D:/aria-agent/.env safely.")

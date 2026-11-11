import os

search_paths = [
    'C:/Users/om',
    'C:/Users/om/.gemini',
    'C:/Users/om/.config',
    'D:/aria-agent'
]

found = []
for sp in search_paths:
    if not os.path.exists(sp): continue
    for root, dirs, files in os.walk(sp):
        if any(skip in root for skip in ['node_modules', '.git', 'site-packages', 'AppData/Local/Temp', '$RECYCLE.BIN']):
            continue
        for f in files:
            if f.endswith(('.env', '.json', '.txt', '.yaml', '.yml')) and any(w in f.lower() for w in ['env', 'key', 'secret', 'config']):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                        for line in fl:
                            l_up = line.upper()
                            if any(k in l_up for k in ['GEMINI_API_KEY', 'GROQ_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']):
                                if '=' in line:
                                    k, v = line.strip().split('=', 1)
                                    if v.strip() and not v.strip().startswith(('your_', 'gsk_your', '""', "''")):
                                        found.append((p, k.strip()))
                except Exception:
                    pass

print("Found configured keys in:")
for p, k in found:
    print(f"  {p} -> {k}")
if not found:
    print("  No configured LLM API keys found on the system.")

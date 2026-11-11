path = 'D:/aria-agent/.github/workflows/aria-24x7-hourly-scraper.yml'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = "        env:\n          TELEGRAM_BOT_TOKEN:"
replacement = """        env:
          GH_TOKEN: ${{ secrets.GH_AGENT_PAT || secrets.GITHUB_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GH_AGENT_PAT || secrets.GITHUB_TOKEN }}
          GH_PAT: ${{ secrets.GH_AGENT_PAT || secrets.GITHUB_TOKEN }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_BOT_TOKEN:"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: updated hourly scraper workflow environment with GH_TOKEN and LLM keys!")
else:
    print("Target string not found in workflow file.")

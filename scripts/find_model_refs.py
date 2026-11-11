with open('D:/aria-agent/src/aria/security/telegram_bot_service.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'llama' in line.lower() or 'model' in line.lower() and 'groq' in line.lower():
            print(f'{i+1}: {line.strip()}')

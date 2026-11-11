fp = "D:/aria-agent/src/aria/security/telegram_bot_service.py"
with open(fp, "r", encoding="utf-8") as f:
    code = f.read()

target = '"model": "llama-3.3-70b-versatile",'
replacement = '''"model": os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),'''

if target in code:
    code = code.replace(target, replacement, 1)

# Also ensure models fallback in Groq call
fallback_target = '''            except Exception as e:
                print(f"[!] Groq inference error: {e}")'''

fallback_replacement = '''            except Exception as e:
                print(f"[!] Groq inference error with primary model: {e}. Trying qwen/qwen3.8-27b...")
                try:
                    payload["model"] = "qwen/qwen3.8-27b"
                    resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
                except Exception as e2:
                    print(f"[!] Groq secondary error: {e2}")'''

if fallback_target in code:
    code = code.replace(fallback_target, fallback_replacement, 1)

with open(fp, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated telegram_bot_service with verified Groq models.")

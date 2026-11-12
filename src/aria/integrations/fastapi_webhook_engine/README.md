# Python FastAPI Webhook & API Integration Engine
**Author:** Hardik Kakkad ([Contra Service Profile](https://contra.com/s/UsUQXXqo-python-fast-api-webhook-and-api-integration))  
**Rate:** Starting at $150 / hr  

---

## 🚀 Features Included
1. **HMAC-SHA256 Signature Verification:**
   - **Stripe**: `Stripe-Signature` timestamped verification (`t=...,v1=...`) with drift window replay defense.
   - **Shopify**: `X-Shopify-Hmac-Sha256` Base64 digest verification.
   - **HubSpot / Twilio / Generic**: Constant-time `hmac.compare_digest` hex verification.
2. **Pydantic V2 Strict Payload Validation:**
   - Full model typing for checkout sessions, payment intents, and order data.
3. **Idempotency & Deduplication:**
   - Guarantees zero duplicate event executions across retries and webhook replays.
4. **Background Task Queue with Exponential Backoff:**
   - Returns `200 OK` in `<50ms` while processing heavy CRM/database updates asynchronously.
5. **Docker & Render Ready:**
   - Production containerization with `Dockerfile` and `render.yaml`.

---

## 🛠️ Quickstart

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Access Swagger UI at: `http://localhost:8000/docs`

---

## 🧪 Testing

```bash
pytest ../../../tests/test_fastapi_webhook_engine.py -v
```

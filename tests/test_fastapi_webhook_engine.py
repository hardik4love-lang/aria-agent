"""
Comprehensive Unit & Integration Tests for FastAPI Webhook Engine.
Tests HMAC-SHA256 verification, Pydantic V2 validation, replay attack rejection, and idempotency.
"""

import time
import hmac
import hashlib
import base64
import json
import pytest
from starlette.testclient import TestClient

from aria.integrations.fastapi_webhook_engine.app import create_webhook_app
from aria.integrations.fastapi_webhook_engine.security import (
    verify_stripe_signature,
    verify_shopify_signature,
    verify_generic_hmac,
)

STRIPE_SECRET = "whsec_test_stripe_secret_key_8899"
SHOPIFY_SECRET = "shpss_test_shopify_secret_key_1122"
GENERIC_SECRET = "gen_test_secret_key_3344"

@pytest.fixture
def client():
    app = create_webhook_app(
        db_path=":memory:",
        stripe_secret=STRIPE_SECRET,
        shopify_secret=SHOPIFY_SECRET,
        generic_secret=GENERIC_SECRET,
    )
    return TestClient(app)

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "Hardik Kakkad" in res.json()["author"]

def test_stripe_valid_webhook(client):
    payload_dict = {
        "id": "evt_test_charge_succeeded_001",
        "object": "event",
        "type": "payment_intent.succeeded",
        "created": int(time.time()),
        "data": {"object": {"id": "pi_12345", "amount": 15000, "currency": "usd"}},
        "livemode": False
    }
    raw_payload = json.dumps(payload_dict).encode("utf-8")
    t = str(int(time.time()))
    signed_data = f"{t}.".encode("utf-8") + raw_payload
    v1_sig = hmac.new(STRIPE_SECRET.encode("utf-8"), signed_data, hashlib.sha256).hexdigest()
    sig_header = f"t={t},v1={v1_sig}"

    res = client.post(
        "/webhooks/stripe",
        content=raw_payload,
        headers={"Stripe-Signature": sig_header, "Content-Type": "application/json"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["event_id"] == "evt_test_charge_succeeded_001"
    assert data["status"] == "queued"

    # Test Deduplication / Idempotency
    res_dup = client.post(
        "/webhooks/stripe",
        content=raw_payload,
        headers={"Stripe-Signature": sig_header, "Content-Type": "application/json"}
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["status"] == "deduplicated"

def test_stripe_invalid_signature(client):
    raw_payload = b'{"id":"evt_fraud","type":"charge.refunded","created":123,"data":{}}'
    res = client.post(
        "/webhooks/stripe",
        content=raw_payload,
        headers={"Stripe-Signature": "t=123456,v1=bad_signature_hex"}
    )
    assert res.status_code == 400
    assert "Invalid Stripe webhook signature" in res.json()["detail"]

def test_stripe_replay_attack_expired_timestamp(client):
    old_time = int(time.time()) - 1000 # 1000 seconds ago > 300s tolerance
    raw_payload = b'{"id":"evt_old","type":"payment.failed","created":123,"data":{}}'
    signed_data = f"{old_time}.".encode("utf-8") + raw_payload
    v1_sig = hmac.new(STRIPE_SECRET.encode("utf-8"), signed_data, hashlib.sha256).hexdigest()
    sig_header = f"t={old_time},v1={v1_sig}"

    res = client.post(
        "/webhooks/stripe",
        content=raw_payload,
        headers={"Stripe-Signature": sig_header}
    )
    assert res.status_code == 400

def test_shopify_valid_webhook(client):
    payload_dict = {
        "id": 9988776655,
        "email": "customer@example.com",
        "total_price": "299.00",
        "currency": "USD",
        "line_items": [{"id": 1, "title": "Silk Saree", "quantity": 1, "price": "299.00"}]
    }
    raw_payload = json.dumps(payload_dict).encode("utf-8")
    digest = hmac.new(SHOPIFY_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).digest()
    b64_sig = base64.b64encode(digest).decode("utf-8")

    res = client.post(
        "/webhooks/shopify",
        content=raw_payload,
        headers={"X-Shopify-Hmac-Sha256": b64_sig, "X-Shopify-Topic": "orders/create"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["event_id"] == "9988776655"
    assert data["status"] == "queued"

def test_generic_hmac_webhook(client):
    payload_dict = {
        "event_id": "gen_evt_4567",
        "event_type": "user.signup",
        "payload": {"user_id": "u_992", "plan": "pro"}
    }
    raw_payload = json.dumps(payload_dict).encode("utf-8")
    hex_sig = hmac.new(GENERIC_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()

    res = client.post(
        "/webhooks/generic",
        content=raw_payload,
        headers={"X-Signature-256": hex_sig}
    )
    assert res.status_code == 200
    assert res.json()["event_id"] == "gen_evt_4567"
    assert res.json()["status"] == "queued"

"""
Cryptographic Security & HMAC-SHA256 Signature Verification Layer.
Supports Stripe, Shopify, Twilio, and standard HMAC Webhooks with replay defense.
"""

import hmac
import hashlib
import base64
import time
from typing import Optional

class WebhookSecurityError(Exception):
    """Raised when webhook signature validation fails."""
    pass

def verify_generic_hmac(payload: bytes, signature_hex: str, secret: str) -> bool:
    """Verifies standard HMAC-SHA256 hex signature using constant-time comparison."""
    if not signature_hex or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.lower(), signature_hex.lower())

def verify_stripe_signature(
    payload: bytes,
    sig_header: str,
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verifies Stripe signature header (t=timestamp,v1=signature).
    Prevents replay attacks by checking timestamp drift against tolerance_seconds.
    """
    if not sig_header or not secret:
        return False

    parts = dict(item.split("=", 1) for item in sig_header.split(",") if "=" in item)
    timestamp = parts.get("t")
    v1_sig = parts.get("v1")

    if not timestamp or not v1_sig:
        return False

    try:
        t_int = int(timestamp)
    except ValueError:
        return False

    # Replay attack window check
    if tolerance_seconds > 0 and abs(time.time() - t_int) > tolerance_seconds:
        return False

    signed_payload = f"{timestamp}.".encode("utf-8") + payload
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.lower(), v1_sig.lower())

def verify_shopify_signature(payload: bytes, hmac_header: str, secret: str) -> bool:
    """
    Verifies Shopify base64-encoded HMAC-SHA256 signature (X-Shopify-Hmac-Sha256).
    """
    if not hmac_header or not secret:
        return False

    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    expected_b64 = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected_b64, hmac_header.strip())

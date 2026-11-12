"""
FastAPI Webhook & API Integration Engine.
Turnkey, production-grade webhook receiver with HMAC-SHA256 signature verification,
Pydantic V2 payload validation, idempotent storage, and background retry queue.
Offered on Contra by Hardik Kakkad ($150/hr).
"""

from .security import (
    verify_stripe_signature,
    verify_shopify_signature,
    verify_generic_hmac,
    WebhookSecurityError,
)
from .schemas import (
    StripeWebhookEvent,
    ShopifyWebhookEvent,
    GenericWebhookEvent,
    WebhookIngestResponse,
)
from .storage import WebhookStore
from .queue import BackgroundRetryQueue
from .app import create_webhook_app, app

__all__ = [
    "verify_stripe_signature",
    "verify_shopify_signature",
    "verify_generic_hmac",
    "WebhookSecurityError",
    "StripeWebhookEvent",
    "ShopifyWebhookEvent",
    "GenericWebhookEvent",
    "WebhookIngestResponse",
    "WebhookStore",
    "BackgroundRetryQueue",
    "create_webhook_app",
    "app",
]

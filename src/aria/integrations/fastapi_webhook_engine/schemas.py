"""
Pydantic V2 Schemas for Inbound Webhooks & Event Payloads.
Ensures strict type-safety, field validation, and clean serialization.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict

class WebhookIngestResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool = Field(default=True, description="Whether the event was successfully ingested")
    event_id: str = Field(description="Unique event ID")
    event_type: str = Field(description="Type of the event, e.g. payment_intent.succeeded")
    status: str = Field(default="queued", description="Status: queued, processed, or deduplicated")
    message: Optional[str] = Field(default=None, description="Descriptive status message")

class GenericWebhookEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str = Field(description="Unique identifier for deduplication")
    event_type: str = Field(description="Type of event")
    timestamp: Optional[int] = Field(default=None, description="Unix timestamp of the event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Raw event payload")

class StripeWebhookEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Stripe event ID (e.g. evt_123...)")
    object: str = Field(default="event")
    type: str = Field(description="Stripe event type (e.g. checkout.session.completed)")
    created: int = Field(description="Creation timestamp")
    data: Dict[str, Any] = Field(description="Event data object containing object details")
    livemode: Optional[bool] = Field(default=False)

class ShopifyLineItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[int] = None
    title: Optional[str] = None
    quantity: Optional[int] = 1
    price: Optional[str] = "0.00"

class ShopifyWebhookEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int = Field(description="Shopify order/product ID")
    email: Optional[str] = None
    total_price: Optional[str] = "0.00"
    currency: Optional[str] = "USD"
    line_items: List[ShopifyLineItem] = Field(default_factory=list)

"""Webhook payload schemas for AiSensy integration.

NOTE: These schemas are based on expected WhatsApp Business API / AiSensy
webhook structures. Exact field names may need adjustment once live
AiSensy credentials and documentation are available.
"""

from pydantic import BaseModel


class WebhookContact(BaseModel):
    """Contact info from webhook payload."""
    wa_id: str  # WhatsApp ID (phone number)
    profile_name: str | None = None


class WebhookMessage(BaseModel):
    """Inbound message from webhook."""
    id: str  # External message ID from AiSensy/WhatsApp
    from_number: str  # Sender phone
    timestamp: str
    type: str = "text"  # text, image, document, etc.
    text: str | None = None
    media_url: str | None = None
    caption: str | None = None


class WebhookStatus(BaseModel):
    """Message status update from webhook."""
    id: str  # External message ID
    status: str  # sent, delivered, read, failed
    timestamp: str
    recipient_id: str | None = None
    errors: list[dict] | None = None


class AiSensyWebhookPayload(BaseModel):
    """Top-level webhook payload from AiSensy.

    TODO: Confirm exact payload structure from AiSensy documentation.
    This is modeled after standard WhatsApp Cloud API webhook format.
    AiSensy may wrap this in their own envelope.
    """
    event_type: str | None = None  # message, status, etc.
    message: WebhookMessage | None = None
    status: WebhookStatus | None = None
    contact: WebhookContact | None = None
    raw_payload: dict | None = None  # Store original for debugging


class OutboundMessageRequest(BaseModel):
    """Request to send a message via AiSensy API."""
    to: str  # Recipient phone number
    message: str
    message_type: str = "text"
    template_name: str | None = None
    template_params: list[str] | None = None
    media_url: str | None = None

"""AiSensy webhook event processing.

Handles inbound messages and delivery status updates from AiSensy webhooks.
Includes idempotency checks and signature verification scaffolding.

TODO: Confirm exact webhook payload format from AiSensy documentation.
The current implementation handles the expected standard WhatsApp webhook patterns.
"""

import hashlib
import hmac

from fastapi import HTTPException, Request

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.webhook import AiSensyWebhookPayload, WebhookMessage, WebhookStatus

logger = get_logger("webhook")
settings = get_settings()


def verify_webhook_signature(request: Request, body: bytes) -> bool:
    """Verify webhook signature if configured.

    TODO: Confirm AiSensy's signature mechanism. This implements
    HMAC-SHA256 which is the standard approach for webhook verification.
    If AiSensy uses a different method, adjust accordingly.
    """
    secret = settings.AISENSY_WEBHOOK_SECRET
    if not secret:
        # Skip verification if no secret configured (dev mode)
        return True

    signature = request.headers.get("X-AiSensy-Signature", "")
    if not signature:
        signature = request.headers.get("X-Hub-Signature-256", "")

    if not signature:
        logger.warning("webhook_no_signature")
        return False

    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    sig_value = signature.replace("sha256=", "")
    return hmac.compare_digest(expected, sig_value)


def parse_webhook_payload(raw: dict) -> AiSensyWebhookPayload:
    """Parse raw webhook JSON into our internal schema.

    TODO: Adjust field mapping once exact AiSensy payload format is confirmed.
    This handles two common patterns:
    1. Direct message/status objects
    2. Nested under entry[].changes[].value (WhatsApp Cloud API style)
    """
    # Try direct format first
    if "message" in raw or "status" in raw:
        return AiSensyWebhookPayload(
            event_type=raw.get("event_type", "message" if "message" in raw else "status"),
            message=WebhookMessage(**raw["message"]) if "message" in raw else None,
            status=WebhookStatus(**raw["status"]) if "status" in raw else None,
            raw_payload=raw,
        )

    # Try WhatsApp Cloud API nested format
    try:
        entries = raw.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                statuses = value.get("statuses", [])

                if messages:
                    msg = messages[0]
                    return AiSensyWebhookPayload(
                        event_type="message",
                        message=WebhookMessage(
                            id=msg.get("id", ""),
                            from_number=msg.get("from", ""),
                            timestamp=msg.get("timestamp", ""),
                            type=msg.get("type", "text"),
                            text=msg.get("text", {}).get("body") if msg.get("type") == "text" else msg.get("caption"),
                            media_url=msg.get(msg.get("type", ""), {}).get("link") if msg.get("type") != "text" else None,
                        ),
                        raw_payload=raw,
                    )

                if statuses:
                    st = statuses[0]
                    return AiSensyWebhookPayload(
                        event_type="status",
                        status=WebhookStatus(
                            id=st.get("id", ""),
                            status=st.get("status", ""),
                            timestamp=st.get("timestamp", ""),
                            recipient_id=st.get("recipient_id"),
                        ),
                        raw_payload=raw,
                    )
    except (KeyError, IndexError, TypeError) as e:
        logger.warning("webhook_parse_fallback", error=str(e))

    # Fallback: store raw payload for later inspection
    logger.warning("webhook_unknown_format", keys=list(raw.keys()))
    return AiSensyWebhookPayload(
        event_type="unknown",
        raw_payload=raw,
    )

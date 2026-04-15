"""WhatsApp webhook endpoint — receives events from AiSensy."""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.integrations.aisensy.client import get_bsp_provider
from app.integrations.aisensy.webhook_handler import parse_webhook_payload, verify_webhook_signature
from app.services.conversation_service import ConversationService
from app.ai.agent import WhatsAppAIAgent
from app.models.conversation import ConversationStatus, MessageStatus
from app.models.lead import Lead

logger = get_logger("webhook")

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/aisensy")
async def webhook_verify(request: Request):
    """Webhook verification endpoint for AiSensy/WhatsApp setup.

    TODO: Confirm AiSensy's verification method. WhatsApp Cloud API uses
    hub.mode, hub.verify_token, hub.challenge query params.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token:
        logger.info("webhook_verification", mode=mode)
        return Response(content=challenge or "OK", media_type="text/plain")

    return Response(content="OK", media_type="text/plain")


@router.post("/aisensy")
async def webhook_receive(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive and process webhook events from AiSensy."""
    body = await request.body()

    # Verify signature
    if not verify_webhook_signature(request, body):
        logger.warning("webhook_signature_invalid")
        return {"status": "signature_invalid"}

    raw = await request.json()
    payload = parse_webhook_payload(raw)

    # Handle message events
    if payload.event_type == "message" and payload.message:
        await _handle_inbound_message(payload.message, db)

    # Handle status updates
    elif payload.event_type == "status" and payload.status:
        await _handle_status_update(payload.status, db)

    else:
        logger.info("webhook_unhandled_event", event_type=payload.event_type)

    return {"status": "ok"}


async def _handle_inbound_message(message, db: AsyncSession):
    """Process an inbound WhatsApp message."""
    conv_service = ConversationService(db)

    # Idempotency check
    if message.id and await conv_service.check_idempotency(message.id):
        logger.info("webhook_duplicate_message", external_id=message.id)
        return

    # Get or create contact and conversation
    contact = await conv_service.get_or_create_contact(
        phone_number=message.from_number,
        name=None,
    )

    if contact.is_blocked:
        logger.info("webhook_blocked_contact", phone=message.from_number[:6] + "****")
        return

    conversation = await conv_service.get_or_create_conversation(contact)

    # Store inbound message
    text_content = message.text or message.caption or f"[{message.type} message]"
    inbound_msg = await conv_service.store_inbound_message(
        conversation=conversation,
        content=text_content,
        external_id=message.id,
        message_type=message.type,
        media_url=message.media_url,
    )

    logger.info(
        "inbound_message_stored",
        conversation_id=str(conversation.id),
        message_id=str(inbound_msg.id),
        type=message.type,
    )

    # Generate AI response if AI is active
    if conversation.is_ai_active and message.type == "text" and message.text:
        try:
            agent = WhatsAppAIAgent(db=db)
            result = await agent.process_message(conversation, message.text)

            # Handle handoff
            if result["should_handoff"]:
                await conv_service.initiate_handoff(
                    conversation_id=conversation.id,
                    reason="AI confidence too low or handoff requested",
                    handoff_type="auto",
                )

            # Send reply via BSP
            bsp = get_bsp_provider()
            try:
                send_result = await bsp.send_message(
                    to=contact.phone_number,
                    message=result["response"],
                )
                external_id = send_result.get("id")
            except Exception as e:
                logger.error("bsp_send_failed", error=str(e))
                external_id = None

            # Store outbound message
            await conv_service.store_outbound_message(
                conversation=conversation,
                content=result["response"],
                is_ai_generated=True,
                ai_run_id=result["ai_run_id"],
                external_id=external_id,
            )

            # Store lead data if captured
            if result.get("lead_data"):
                lead = Lead(
                    contact_id=contact.id,
                    conversation_id=conversation.id,
                    **result["lead_data"],
                )
                db.add(lead)

        except Exception as e:
            logger.error(
                "ai_processing_failed",
                conversation_id=str(conversation.id),
                error=str(e),
            )


async def _handle_status_update(status, db: AsyncSession):
    """Process a message delivery status update."""
    from sqlalchemy import select
    from app.models.conversation import Message, MessageEvent

    # Find the message by external ID
    stmt = select(Message).where(Message.external_id == status.id)
    result = await db.execute(stmt)
    msg = result.scalar_one_or_none()

    if not msg:
        logger.debug("status_update_no_matching_message", external_id=status.id)
        return

    # Map status
    status_map = {
        "sent": MessageStatus.SENT,
        "delivered": MessageStatus.DELIVERED,
        "read": MessageStatus.READ,
        "failed": MessageStatus.FAILED,
    }
    new_status = status_map.get(status.status)
    if new_status:
        msg.status = new_status

    # Log the event
    event = MessageEvent(
        message_id=msg.id,
        event_type=status.status,
        external_id=status.id,
        payload={"recipient_id": status.recipient_id, "errors": status.errors},
    )
    db.add(event)

    logger.info("status_update_processed", message_id=str(msg.id), status=status.status)

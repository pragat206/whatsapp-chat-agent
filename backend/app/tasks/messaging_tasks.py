"""Background tasks for message processing and retries."""

import asyncio
import uuid

from app.core.database import async_session_factory
from app.core.logging import get_logger
from app.tasks.celery_app import celery_app

logger = get_logger("tasks.messaging")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def retry_failed_message(self, message_id: str):
    """Retry sending a failed outbound message."""

    async def _run():
        async with async_session_factory() as session:
            from sqlalchemy import select
            from app.models.conversation import Message, MessageStatus, Conversation
            from app.models.contact import Contact
            from app.integrations.aisensy.client import get_bsp_provider

            stmt = (
                select(Message)
                .where(Message.id == uuid.UUID(message_id))
            )
            result = await session.execute(stmt)
            msg = result.scalar_one_or_none()

            if not msg or msg.status != MessageStatus.FAILED:
                return

            # Get conversation and contact
            conv_stmt = select(Conversation).where(Conversation.id == msg.conversation_id)
            conv_result = await session.execute(conv_stmt)
            conv = conv_result.scalar_one_or_none()

            if not conv:
                return

            contact_stmt = select(Contact).where(Contact.id == conv.contact_id)
            contact_result = await session.execute(contact_stmt)
            contact = contact_result.scalar_one_or_none()

            if not contact:
                return

            try:
                bsp = get_bsp_provider()
                result = await bsp.send_message(to=contact.phone_number, message=msg.content)
                msg.external_id = result.get("id")
                msg.status = MessageStatus.SENT
                await session.commit()
                logger.info("message_retry_success", message_id=message_id)
            except Exception as e:
                await session.rollback()
                logger.error("message_retry_failed", message_id=message_id, error=str(e))
                raise self.retry(exc=e)

    asyncio.run(_run())

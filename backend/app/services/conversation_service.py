"""Conversation management service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contact import Contact
from app.models.conversation import (
    Conversation,
    ConversationNote,
    ConversationStatus,
    HandoffEvent,
    Message,
    MessageDirection,
    MessageStatus,
    Tag,
)


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_contact(self, phone_number: str, name: str | None = None) -> Contact:
        stmt = select(Contact).where(Contact.phone_number == phone_number)
        result = await self.db.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            contact = Contact(
                phone_number=phone_number,
                display_name=name,
                whatsapp_name=name,
            )
            self.db.add(contact)
            await self.db.flush()

        return contact

    async def get_or_create_conversation(self, contact: Contact) -> Conversation:
        stmt = (
            select(Conversation)
            .where(
                Conversation.contact_id == contact.id,
                Conversation.status.in_([
                    ConversationStatus.ACTIVE,
                    ConversationStatus.WAITING,
                    ConversationStatus.HANDOFF,
                ]),
            )
            .options(selectinload(Conversation.contact), selectinload(Conversation.tags))
            .order_by(Conversation.created_at.desc())
        )
        result = await self.db.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                contact_id=contact.id,
                language=contact.language or "en",
            )
            self.db.add(conversation)
            await self.db.flush()

        return conversation

    async def store_inbound_message(
        self,
        conversation: Conversation,
        content: str,
        external_id: str | None = None,
        message_type: str = "text",
        media_url: str | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation.id,
            direction=MessageDirection.INBOUND,
            message_type=message_type,
            content=content,
            status=MessageStatus.DELIVERED,
            external_id=external_id,
            media_url=media_url,
        )
        self.db.add(msg)

        conversation.message_count = (conversation.message_count or 0) + 1
        conversation.last_message_at = datetime.now(timezone.utc)
        if conversation.status == ConversationStatus.RESOLVED:
            conversation.status = ConversationStatus.ACTIVE

        await self.db.flush()
        return msg

    async def store_outbound_message(
        self,
        conversation: Conversation,
        content: str,
        is_ai_generated: bool = False,
        ai_run_id: uuid.UUID | None = None,
        external_id: str | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation.id,
            direction=MessageDirection.OUTBOUND,
            content=content,
            status=MessageStatus.PENDING,
            is_ai_generated=is_ai_generated,
            ai_run_id=ai_run_id,
            external_id=external_id,
        )
        self.db.add(msg)
        conversation.message_count = (conversation.message_count or 0) + 1
        conversation.last_message_at = datetime.now(timezone.utc)
        await self.db.flush()
        return msg

    async def list_conversations(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Conversation], int]:
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.contact), selectinload(Conversation.tags))
            .order_by(Conversation.last_message_at.desc().nullslast())
        )
        count_stmt = select(func.count(Conversation.id))

        if status:
            stmt = stmt.where(Conversation.status == status)
            count_stmt = count_stmt.where(Conversation.status == status)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        conversations = list(result.scalars().all())

        return conversations, total

    async def get_conversation_detail(self, conversation_id: uuid.UUID) -> Conversation | None:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(
                selectinload(Conversation.contact),
                selectinload(Conversation.messages),
                selectinload(Conversation.tags),
                selectinload(Conversation.notes),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_conversation(
        self,
        conversation_id: uuid.UUID,
        **kwargs,
    ) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(stmt)
        conv = result.scalar_one_or_none()
        if not conv:
            return None

        for key, value in kwargs.items():
            if key == "tag_ids":
                tag_stmt = select(Tag).where(Tag.id.in_(value))
                tag_result = await self.db.execute(tag_stmt)
                conv.tags = list(tag_result.scalars().all())
            elif hasattr(conv, key) and value is not None:
                setattr(conv, key, value)

        await self.db.flush()
        return conv

    async def initiate_handoff(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        reason: str | None = None,
        handoff_type: str = "manual",
    ) -> HandoffEvent:
        conv = await self.update_conversation(
            conversation_id,
            status=ConversationStatus.HANDOFF,
            is_ai_active=False,
        )

        event = HandoffEvent(
            conversation_id=conversation_id,
            initiated_by=user_id,
            reason=reason,
            handoff_type=handoff_type,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def resume_ai(self, conversation_id: uuid.UUID) -> Conversation | None:
        return await self.update_conversation(
            conversation_id,
            status=ConversationStatus.ACTIVE,
            is_ai_active=True,
        )

    async def add_note(
        self,
        conversation_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
    ) -> ConversationNote:
        note = ConversationNote(
            conversation_id=conversation_id,
            author_id=author_id,
            content=content,
        )
        self.db.add(note)
        await self.db.flush()
        return note

    async def check_idempotency(self, external_id: str) -> bool:
        """Return True if message with this external_id already exists."""
        stmt = select(Message.id).where(Message.external_id == external_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

"""Conversation and Message models."""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    WAITING = "waiting"
    HANDOFF = "handoff"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ConversationState(str, enum.Enum):
    FAQ = "faq"
    LEAD_QUALIFICATION = "lead_qualification"
    SUPPORT = "support"
    HUMAN_HANDOFF = "human_handoff"
    GREETING = "greeting"
    IDLE = "idle"


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"


conversation_tags = Table(
    "conversation_tags",
    BaseModel.metadata,
    Column(
        "conversation_id",
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
    ),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE")),
)


class Tag(BaseModel):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")


class Conversation(BaseModel):
    __tablename__ = "conversations"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False, index=True
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), default=ConversationStatus.ACTIVE, index=True
    )
    state: Mapped[ConversationState] = mapped_column(
        Enum(ConversationState), default=ConversationState.GREETING
    )
    is_ai_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    contact: Mapped["Contact"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", order_by="Message.created_at"
    )
    tags: Mapped[list[Tag]] = relationship(secondary=conversation_tags, lazy="selectin")
    handoff_events: Mapped[list["HandoffEvent"]] = relationship(back_populates="conversation")
    notes: Mapped[list["ConversationNote"]] = relationship(back_populates="conversation")

    def __repr__(self) -> str:
        return f"<Conversation {self.id} status={self.status}>"


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True
    )
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection), nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.TEXT
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), default=MessageStatus.PENDING
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_runs.id"), nullable=True
    )
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class MessageEvent(BaseModel):
    """Tracks delivery status updates from the BSP."""

    __tablename__ = "message_events"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    timestamp: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class HandoffEvent(BaseModel):
    __tablename__ = "handoff_events"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    initiated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    handoff_type: Mapped[str] = mapped_column(String(50), default="manual")
    resolved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation: Mapped[Conversation] = relationship(back_populates="handoff_events")


class ConversationNote(BaseModel):
    __tablename__ = "conversation_notes"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

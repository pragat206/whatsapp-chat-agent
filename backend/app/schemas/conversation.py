"""Conversation and message schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    message_type: str
    content: str
    status: str
    external_id: str | None = None
    is_ai_generated: bool = False
    media_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactBrief(BaseModel):
    id: uuid.UUID
    phone_number: str
    display_name: str | None = None
    city: str | None = None
    language: str = "en"

    model_config = {"from_attributes": True}


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str = "#6366f1"

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: uuid.UUID
    contact: ContactBrief
    status: str
    state: str
    is_ai_active: bool
    assigned_to: uuid.UUID | None = None
    language: str
    message_count: int
    last_message_at: datetime | None = None
    tags: list[TagOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class ConversationListOut(BaseModel):
    conversations: list[ConversationOut]
    total: int


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HandoffRequest(BaseModel):
    reason: str | None = None


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = "#6366f1"


class ConversationUpdate(BaseModel):
    status: str | None = None
    state: str | None = None
    is_ai_active: bool | None = None
    assigned_to: uuid.UUID | None = None
    tag_ids: list[uuid.UUID] | None = None


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    message_type: str = "text"

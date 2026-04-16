"""All models re-exported for Alembic and convenience."""

from app.models.ai_run import AIRun
from app.models.audit import AuditLog, BackgroundJob, Setting
from app.models.base import BaseModel
from app.models.contact import Contact
from app.models.conversation import (
    Conversation,
    ConversationNote,
    ConversationState,
    ConversationStatus,
    HandoffEvent,
    Message,
    MessageDirection,
    MessageEvent,
    MessageStatus,
    MessageType,
    Tag,
)
from app.models.knowledge import EmbeddingRecord, KnowledgeChunk, KnowledgeSource, SourceStatus, SourceType
from app.models.lead import Lead
from app.models.product import Product, ProductCategory
from app.models.user import Role, User

__all__ = [
    "AIRun",
    "AuditLog",
    "BackgroundJob",
    "BaseModel",
    "Contact",
    "Conversation",
    "ConversationNote",
    "ConversationState",
    "ConversationStatus",
    "EmbeddingRecord",
    "HandoffEvent",
    "KnowledgeChunk",
    "KnowledgeSource",
    "Lead",
    "Message",
    "MessageDirection",
    "MessageEvent",
    "MessageStatus",
    "MessageType",
    "Product",
    "ProductCategory",
    "Role",
    "Setting",
    "SourceStatus",
    "SourceType",
    "Tag",
    "User",
]

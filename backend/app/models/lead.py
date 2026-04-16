"""Lead model for captured prospect information."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True
    )
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_interest: Mapped[str | None] = mapped_column(String(500), nullable=True)
    budget: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_preference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_fields: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    contact: Mapped["Contact"] = relationship(back_populates="leads")

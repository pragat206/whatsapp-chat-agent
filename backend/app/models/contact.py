"""Contact model — represents a WhatsApp end-user."""

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    whatsapp_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    tags: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="contact")
    leads: Mapped[list["Lead"]] = relationship(back_populates="contact")

    def __repr__(self) -> str:
        return f"<Contact {self.phone_number}>"

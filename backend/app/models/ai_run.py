"""AI run tracking — logs every LLM call for observability."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AIRun(BaseModel):
    __tablename__ = "ai_runs"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_chunks: Mapped[dict | None] = mapped_column(JSONB, default=list)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

"""Knowledge source and chunk models for RAG pipeline."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SourceType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    MANUAL = "manual"
    URL = "url"


class SourceStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DEACTIVATED = "deactivated"


class KnowledgeSource(BaseModel):
    __tablename__ = "knowledge_sources"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus), default=SourceStatus.PENDING
    )
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    product: Mapped["Product | None"] = relationship(back_populates="knowledge_sources")
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class KnowledgeChunk(BaseModel):
    __tablename__ = "knowledge_chunks"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    source: Mapped[KnowledgeSource] = relationship(back_populates="chunks")
    embedding: Mapped["EmbeddingRecord | None"] = relationship(
        back_populates="chunk", uselist=False
    )


class EmbeddingRecord(BaseModel):
    """Stores embedding vector reference. Actual vector in pgvector column."""

    __tablename__ = "embedding_records"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    # The actual vector is stored via pgvector; see migration for column type
    # We reference it here for ORM tracking

    chunk: Mapped[KnowledgeChunk] = relationship(back_populates="embedding")

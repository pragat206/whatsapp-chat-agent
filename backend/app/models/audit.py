"""Audit log and settings models."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Setting(BaseModel):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="general")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class BackgroundJob(BaseModel):
    __tablename__ = "background_jobs"

    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)

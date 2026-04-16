"""Knowledge source schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    source_type: str
    product_id: uuid.UUID | None = None
    content_text: str | None = None
    url: str | None = None


class KnowledgeSourceOut(BaseModel):
    id: uuid.UUID
    title: str
    source_type: str
    status: str
    file_path: str | None = None
    file_size: int | None = None
    original_filename: str | None = None
    product_id: uuid.UUID | None = None
    chunk_count: int = 0
    version: int = 1
    is_active: bool = True
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeSourceListOut(BaseModel):
    sources: list[KnowledgeSourceOut]
    total: int


class ManualKnowledgeCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=10)
    product_id: uuid.UUID | None = None

"""Product and category schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    parent_id: uuid.UUID | None = None


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    sku: str | None = None
    description: str | None = None
    category_ids: list[uuid.UUID] = []
    metadata: dict | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    description: str | None = None
    is_active: bool | None = None
    category_ids: list[uuid.UUID] | None = None


class ProductOut(BaseModel):
    id: uuid.UUID
    name: str
    sku: str | None = None
    description: str | None = None
    is_active: bool = True
    categories: list[CategoryOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListOut(BaseModel):
    products: list[ProductOut]
    total: int

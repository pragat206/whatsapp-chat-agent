"""Product and category models."""

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

product_categories_assoc = Table(
    "product_category_links",
    BaseModel.metadata,
    Column(
        "product_id",
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
    ),
    Column(
        "category_id",
        UUID(as_uuid=True),
        ForeignKey("product_categories.id", ondelete="CASCADE"),
    ),
)


class ProductCategory(BaseModel):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_categories_assoc, back_populates="categories"
    )


class Product(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    categories: Mapped[list[ProductCategory]] = relationship(
        secondary=product_categories_assoc, back_populates="products", lazy="selectin"
    )
    knowledge_sources: Mapped[list["KnowledgeSource"]] = relationship(back_populates="product")

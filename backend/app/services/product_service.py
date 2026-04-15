"""Product and category management service."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductCategory


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(
        self,
        name: str,
        sku: str | None = None,
        description: str | None = None,
        category_ids: list[uuid.UUID] | None = None,
        metadata: dict | None = None,
    ) -> Product:
        product = Product(name=name, sku=sku, description=description, metadata_=metadata or {})

        if category_ids:
            stmt = select(ProductCategory).where(ProductCategory.id.in_(category_ids))
            result = await self.db.execute(stmt)
            product.categories = list(result.scalars().all())

        self.db.add(product)
        await self.db.flush()
        return product

    async def list_products(
        self, active_only: bool = True, limit: int = 50, offset: int = 0
    ) -> tuple[list[Product], int]:
        stmt = select(Product).options(selectinload(Product.categories))
        count_stmt = select(func.count(Product.id))

        if active_only:
            stmt = stmt.where(Product.is_active.is_(True))
            count_stmt = count_stmt.where(Product.is_active.is_(True))

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.order_by(Product.name).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_product(self, product_id: uuid.UUID) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.categories))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_product(self, product_id: uuid.UUID, **kwargs) -> Product | None:
        product = await self.get_product(product_id)
        if not product:
            return None

        category_ids = kwargs.pop("category_ids", None)
        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        if category_ids is not None:
            stmt = select(ProductCategory).where(ProductCategory.id.in_(category_ids))
            result = await self.db.execute(stmt)
            product.categories = list(result.scalars().all())

        await self.db.flush()
        return product

    async def create_category(
        self,
        name: str,
        description: str | None = None,
        parent_id: uuid.UUID | None = None,
    ) -> ProductCategory:
        category = ProductCategory(name=name, description=description, parent_id=parent_id)
        self.db.add(category)
        await self.db.flush()
        return category

    async def list_categories(self) -> list[ProductCategory]:
        stmt = select(ProductCategory).where(ProductCategory.is_active.is_(True)).order_by(ProductCategory.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

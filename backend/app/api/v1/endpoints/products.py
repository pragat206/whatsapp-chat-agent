"""Product and category management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.product import (
    CategoryCreate,
    CategoryOut,
    ProductCreate,
    ProductListOut,
    ProductOut,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListOut)
async def list_products(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = ProductService(db)
    products, total = await service.list_products(limit=limit, offset=offset)
    return ProductListOut(products=products, total=total)


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    service = ProductService(db)
    product = await service.create_product(
        name=body.name,
        sku=body.sku,
        description=body.description,
        category_ids=body.category_ids,
        metadata=body.metadata,
    )
    return product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: uuid.UUID,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    service = ProductService(db)
    product = await service.update_product(product_id, **body.model_dump(exclude_none=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# --- Categories ---

@router.get("/categories/list", response_model=list[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = ProductService(db)
    return await service.list_categories()


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(
    body: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    service = ProductService(db)
    return await service.create_category(
        name=body.name,
        description=body.description,
        parent_id=body.parent_id,
    )

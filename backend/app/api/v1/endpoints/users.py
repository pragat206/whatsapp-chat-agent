"""User management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserListOut, UserOut, UserUpdate
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListOut)
async def list_users(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar() or 0

    stmt = (
        select(User)
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    users = list(result.scalars().all())
    return UserListOut(users=users, total=total)


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # Check if email exists
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    service = AuthService(db)
    user = await service.create_user(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        role_names=body.role_names,
    )

    audit = AuditService(db)
    await audit.log(
        action="user_created",
        resource_type="user",
        resource_id=str(user.id),
        user_id=admin.id,
    )

    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role_names is not None:
        role_stmt = select(Role).where(Role.name.in_(body.role_names))
        role_result = await db.execute(role_stmt)
        user.roles = list(role_result.scalars().all())

    await db.flush()

    audit = AuditService(db)
    await audit.log(
        action="user_updated",
        resource_type="user",
        resource_id=str(user.id),
        user_id=admin.id,
        details=body.model_dump(exclude_none=True),
    )

    return user


@router.get("/roles")
async def list_roles(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    return [{"id": r.id, "name": r.name, "description": r.description} for r in roles]

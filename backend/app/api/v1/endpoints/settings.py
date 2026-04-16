"""Settings and audit log endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.audit import AuditLog, Setting
from app.schemas.settings import AuditLogListOut, AuditLogOut, SettingOut, SettingUpdate

router = APIRouter(tags=["settings"])


# --- Settings ---

settings_router = APIRouter(prefix="/settings")


@settings_router.get("", response_model=list[SettingOut])
async def list_settings(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(Setting).order_by(Setting.category, Setting.key)
    if category:
        stmt = stmt.where(Setting.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@settings_router.put("/{key}", response_model=SettingOut)
async def update_setting(
    key: str,
    body: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(Setting).where(Setting.key == key)
    result = await db.execute(stmt)
    setting = result.scalar_one_or_none()

    if not setting:
        setting = Setting(key=key)
        db.add(setting)

    if body.value is not None:
        setting.value = body.value
    if body.value_json is not None:
        setting.value_json = body.value_json

    await db.flush()
    return setting


# --- Audit Logs ---

audit_router = APIRouter(prefix="/audit-logs")


@audit_router.get("", response_model=AuditLogListOut)
async def list_audit_logs(
    action: str | None = None,
    resource_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    count_stmt = select(func.count(AuditLog.id))

    if action:
        stmt = stmt.where(AuditLog.action == action)
        count_stmt = count_stmt.where(AuditLog.action == action)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
        count_stmt = count_stmt.where(AuditLog.resource_type == resource_type)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    logs = list(result.scalars().all())

    return AuditLogListOut(logs=logs, total=total)


# Combine routers
router.include_router(settings_router)
router.include_router(audit_router)

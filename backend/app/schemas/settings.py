"""Settings schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class SettingOut(BaseModel):
    id: uuid.UUID
    key: str
    value: str | None = None
    value_json: dict | None = None
    category: str
    description: str | None = None

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: str | None = None
    value_json: dict | None = None


class AuditLogOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListOut(BaseModel):
    logs: list[AuditLogOut]
    total: int

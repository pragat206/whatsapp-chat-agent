"""User and role schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)
    role_names: list[str] = ["operator"]


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    role_names: list[str] | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[RoleOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    users: list[UserOut]
    total: int

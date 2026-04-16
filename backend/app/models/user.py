"""User and Role models for auth/RBAC."""

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE")),
)


class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates="roles", lazy="selectin"
    )


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        secondary=user_roles, back_populates="users", lazy="selectin"
    )

    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]

    def has_role(self, role_name: str) -> bool:
        return role_name in self.role_names

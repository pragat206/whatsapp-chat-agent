"""Authentication service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import Role, User
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, email: str, password: str) -> TokenResponse | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.roles))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None

        return TokenResponse(
            access_token=create_access_token(
                str(user.id), extra={"roles": user.role_names}
            ),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse | None:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        return TokenResponse(
            access_token=create_access_token(
                str(user.id), extra={"roles": user.role_names}
            ),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role_names: list[str] | None = None,
    ) -> User:
        hashed = hash_password(password)
        user = User(email=email, hashed_password=hashed, full_name=full_name)

        if role_names:
            stmt = select(Role).where(Role.name.in_(role_names))
            result = await self.db.execute(stmt)
            roles = result.scalars().all()
            user.roles = list(roles)

        self.db.add(user)
        await self.db.flush()
        return user

    async def initiate_password_reset(self, email: str) -> str | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None

        token = str(uuid.uuid4())
        user.password_reset_token = token
        await self.db.flush()
        # In production: send email with reset link
        return token

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        stmt = select(User).where(User.password_reset_token == token)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.hashed_password = hash_password(new_password)
        user.password_reset_token = None
        await self.db.flush()
        return True

"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.authenticate(body.email, body.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.refresh_tokens(body.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return result


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/password-reset/request", status_code=202)
async def request_password_reset(
    body: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    await service.initiate_password_reset(body.email)
    # Always return 202 to avoid email enumeration
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    success = await service.confirm_password_reset(body.token, body.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"message": "Password reset successfully"}

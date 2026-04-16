"""Health check, readiness, and metrics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "whatsapp-ai-agent"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    is_ready = db_status == "ok"
    return {
        "ready": is_ready,
        "checks": {"database": db_status},
    }


@router.get("/live")
async def liveness_check():
    return {"alive": True}

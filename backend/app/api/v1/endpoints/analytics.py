"""Analytics and dashboard API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.analytics import AnalyticsResponse, DashboardKPIs
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpis", response_model=DashboardKPIs)
async def get_kpis(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    service = AnalyticsService(db)
    return await service.get_dashboard_kpis(date_from, date_to)


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    service = AnalyticsService(db)
    return await service.get_analytics(date_from, date_to)


@router.get("/trends")
async def get_trends(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    service = AnalyticsService(db)
    trends = await service.get_conversation_trends(date_from, date_to)
    return {"trends": trends}

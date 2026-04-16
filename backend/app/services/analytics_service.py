"""Analytics and dashboard metrics service."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import case, cast, func, select, text, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
    MessageDirection,
    MessageStatus,
)
from app.models.lead import Lead
from app.schemas.analytics import (
    AnalyticsResponse,
    ConversationTrend,
    DashboardKPIs,
    ProductInquiry,
    TopQuestion,
)


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_kpis(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> DashboardKPIs:
        if not date_from:
            date_from = datetime.now(timezone.utc) - timedelta(days=30)
        if not date_to:
            date_to = datetime.now(timezone.utc)

        # Total conversations in period
        conv_count = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.created_at.between(date_from, date_to)
            )
        )
        total_conversations = conv_count.scalar() or 0

        # Active conversations
        active_count = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.status == ConversationStatus.ACTIVE
            )
        )
        active_conversations = active_count.scalar() or 0

        # Resolved conversations
        resolved_count = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.status.in_([ConversationStatus.RESOLVED, ConversationStatus.CLOSED]),
                Conversation.created_at.between(date_from, date_to),
            )
        )
        resolved_conversations = resolved_count.scalar() or 0

        # Messages
        inbound_count = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.direction == MessageDirection.INBOUND,
                Message.created_at.between(date_from, date_to),
            )
        )
        total_inbound = inbound_count.scalar() or 0

        outbound_count = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.direction == MessageDirection.OUTBOUND,
                Message.created_at.between(date_from, date_to),
            )
        )
        total_outbound = outbound_count.scalar() or 0

        # AI vs human handled
        ai_count = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.is_ai_generated.is_(True),
                Message.direction == MessageDirection.OUTBOUND,
                Message.created_at.between(date_from, date_to),
            )
        )
        ai_handled = ai_count.scalar() or 0

        human_handled = total_outbound - ai_handled

        # Escalated
        escalated = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.status == ConversationStatus.HANDOFF,
                Conversation.created_at.between(date_from, date_to),
            )
        )
        escalated_count = escalated.scalar() or 0

        # Leads captured
        leads = await self.db.execute(
            select(func.count(Lead.id)).where(
                Lead.created_at.between(date_from, date_to)
            )
        )
        leads_captured = leads.scalar() or 0

        # Failed messages
        failed = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.status == MessageStatus.FAILED,
                Message.created_at.between(date_from, date_to),
            )
        )
        failed_messages = failed.scalar() or 0

        ai_resolution_rate = (
            (ai_handled / total_outbound * 100) if total_outbound > 0 else 0.0
        )

        return DashboardKPIs(
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            resolved_conversations=resolved_conversations,
            total_inbound_messages=total_inbound,
            total_outbound_messages=total_outbound,
            ai_handled_count=ai_handled,
            human_handled_count=human_handled,
            ai_resolution_rate=round(ai_resolution_rate, 1),
            leads_captured=leads_captured,
            escalated_count=escalated_count,
            failed_messages=failed_messages,
        )

    async def get_conversation_trends(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        granularity: str = "day",
    ) -> list[ConversationTrend]:
        if not date_from:
            date_from = datetime.now(timezone.utc) - timedelta(days=30)
        if not date_to:
            date_to = datetime.now(timezone.utc)

        date_col = cast(Message.created_at, Date)
        stmt = (
            select(
                date_col.label("date"),
                func.count(case((Message.direction == MessageDirection.INBOUND, 1))).label("inbound"),
                func.count(case((Message.direction == MessageDirection.OUTBOUND, 1))).label("outbound"),
                func.count(case((Message.is_ai_generated.is_(True), 1))).label("ai_handled"),
                func.count(
                    case(
                        (
                            (Message.direction == MessageDirection.OUTBOUND)
                            & (Message.is_ai_generated.is_(False)),
                            1,
                        )
                    )
                ).label("human_handled"),
            )
            .where(Message.created_at.between(date_from, date_to))
            .group_by(date_col)
            .order_by(date_col)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            ConversationTrend(
                date=str(row.date),
                inbound=row.inbound,
                outbound=row.outbound,
                ai_handled=row.ai_handled,
                human_handled=row.human_handled,
            )
            for row in rows
        ]

    async def get_analytics(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AnalyticsResponse:
        kpis = await self.get_dashboard_kpis(date_from, date_to)
        trends = await self.get_conversation_trends(date_from, date_to)

        return AnalyticsResponse(
            kpis=kpis,
            trends=trends,
            top_questions=[],
            product_inquiries=[],
        )

"""Analytics and dashboard schemas."""

from datetime import datetime

from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    total_conversations: int = 0
    active_conversations: int = 0
    resolved_conversations: int = 0
    total_inbound_messages: int = 0
    total_outbound_messages: int = 0
    ai_handled_count: int = 0
    human_handled_count: int = 0
    ai_resolution_rate: float = 0.0
    avg_first_response_ms: float | None = None
    avg_resolution_time_ms: float | None = None
    leads_captured: int = 0
    escalated_count: int = 0
    unanswered_count: int = 0
    failed_messages: int = 0


class ConversationTrend(BaseModel):
    date: str
    inbound: int = 0
    outbound: int = 0
    ai_handled: int = 0
    human_handled: int = 0


class TopQuestion(BaseModel):
    question: str
    count: int


class ProductInquiry(BaseModel):
    product_name: str
    inquiry_count: int


class AnalyticsResponse(BaseModel):
    kpis: DashboardKPIs
    trends: list[ConversationTrend] = []
    top_questions: list[TopQuestion] = []
    product_inquiries: list[ProductInquiry] = []


class AnalyticsFilter(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None
    product_id: str | None = None
    status: str | None = None
    handled_by: str | None = None  # "ai" or "human"
    language: str | None = None

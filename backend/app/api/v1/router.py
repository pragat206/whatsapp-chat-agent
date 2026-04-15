"""API v1 router — aggregates all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, conversations, health, knowledge, products, settings, users, webhook

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(conversations.router)
api_router.include_router(products.router)
api_router.include_router(knowledge.router)
api_router.include_router(analytics.router)
api_router.include_router(settings.router)
api_router.include_router(webhook.router)

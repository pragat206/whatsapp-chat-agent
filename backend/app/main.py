"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    setup_logging()

    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            traces_sample_rate=0.1 if settings.is_production else 1.0,
        )

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    setup_middleware(app)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


app = create_app()

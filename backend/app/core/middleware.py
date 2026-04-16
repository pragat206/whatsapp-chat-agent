"""Application middleware: CORS, request ID, rate limiting."""

import time

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import generate_request_id, get_logger, request_id_ctx

logger = get_logger("middleware")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID", generate_request_id())
        request_id_ctx.set(rid)
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = rid
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=elapsed_ms,
        )
        return response


class WebhookRateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter for webhook endpoints."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/webhook"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window
        hits = self._requests.get(client_ip, [])
        hits = [t for t in hits if t > window_start]

        if len(hits) >= self.max_requests:
            logger.warning("rate_limit_exceeded", ip=client_ip, path=request.url.path)
            return Response(content="Rate limit exceeded", status_code=429)

        hits.append(now)
        self._requests[client_ip] = hits
        return await call_next(request)


def setup_middleware(app: FastAPI):
    from fastapi.middleware.cors import CORSMiddleware

    from app.core.config import get_settings

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(WebhookRateLimitMiddleware, max_requests=200, window_seconds=60)

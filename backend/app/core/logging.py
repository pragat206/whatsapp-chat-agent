"""Structured logging setup with correlation IDs and PII masking."""

import re
import uuid
from contextvars import ContextVar

import structlog

from app.core.config import get_settings

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

PII_PATTERNS = [
    (re.compile(r"\b\d{10,13}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL_REDACTED]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE), "Bearer [TOKEN_REDACTED]"),
    (re.compile(r"(password|secret|api_key|token)\s*[:=]\s*\S+", re.IGNORECASE), r"\1=[REDACTED]"),
]


def mask_pii(message: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


def add_request_id(logger, method_name, event_dict):
    rid = request_id_ctx.get("")
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def pii_masker(logger, method_name, event_dict):
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = mask_pii(event_dict["event"])
    return event_dict


def generate_request_id() -> str:
    return str(uuid.uuid4())[:12]


def setup_logging():
    settings = get_settings()
    processors = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        pii_masker,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            structlog.get_level_from_name(settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app"):
    return structlog.get_logger(name)

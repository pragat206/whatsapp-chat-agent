"""Application configuration loaded from environment variables."""

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


def _parse_comma_or_json(v: Any) -> list[str]:
    """Parse a value that's either JSON array or comma-separated string."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [s.strip() for s in v.split(",") if s.strip()]
    return []


class Settings(BaseSettings):
    # App
    APP_NAME: str = "WhatsApp AI Agent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: str = '["*"]'
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_agent"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # JWT
    JWT_SECRET_KEY: str = "change-me-jwt"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AiSensy
    AISENSY_API_KEY: str = ""
    AISENSY_API_BASE_URL: str = "https://backend.aisensy.com"
    AISENSY_PROJECT_ID: str = ""
    AISENSY_WEBHOOK_SECRET: str = ""

    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"
    S3_BUCKET_NAME: str = ""
    S3_REGION: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT_URL: str = ""

    # Observability
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Business
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,hi"
    BUSINESS_HOURS_START: str = "09:00"
    BUSINESS_HOURS_END: str = "18:00"
    BUSINESS_TIMEZONE: str = "Asia/Kolkata"
    MAX_UPLOAD_SIZE_MB: int = 50

    @property
    def cors_origins_list(self) -> list[str]:
        return _parse_comma_or_json(self.CORS_ORIGINS)

    @property
    def allowed_hosts_list(self) -> list[str]:
        return _parse_comma_or_json(self.ALLOWED_HOSTS)

    @property
    def supported_languages_list(self) -> list[str]:
        return _parse_comma_or_json(self.SUPPORTED_LANGUAGES)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()

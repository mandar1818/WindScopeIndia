from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "WindScope India — Renewable Energy Intelligence Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database Configuration (PostgreSQL in production, SQLite fallback for local development)
    DATABASE_URL: str = "sqlite:///./windscope_india.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DATABASE_SSL_MODE: str = "prefer"
    APP_ENV: str = "development"
    INGESTION_ADMIN_KEY: str = "dev-ingestion-admin-key"
    TIMEZONE_IST: str = "Asia/Kolkata"
    MARKET_TIMEZONE: str = "Asia/Kolkata"

    # Evaluation scope constraints
    TARGET_YEAR: int = 2026
    TARGET_MONTH: int = 1
    DEFAULT_DATE: str = "2024-06-01"

    # Local Cache Configuration (in-memory & disk cache)
    CACHE_DIR: str = ".cache"
    CACHE_TTL_SECONDS: int = 3600  # 1 hour cache for historical API payloads

    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                import json
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        return v

    # Explicit Demo fallback mode if external API is unreachable
    ALLOW_DEMO_FALLBACK: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


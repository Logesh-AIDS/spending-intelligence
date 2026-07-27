"""
Centralised configuration — reads from environment variables.
All settings have safe defaults for local development.
"""
import os
from pathlib import Path
from typing import List


class Settings:
    # ── Environment ───────────────────────────────────────────────
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # ── Security ──────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production-must-be-long"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    ALGORITHM: str = "HS256"

    # ── Database ──────────────────────────────────────────────────
    # Falls back to SQLite for local dev; use PostgreSQL in production
    _db_path = Path(__file__).parent.parent.parent.parent / "spending.db"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{_db_path}"
    )

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

    # ── CORS ──────────────────────────────────────────────────────
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000"
        )
        return [o.strip() for o in origins.split(",")]

    # ── ML ────────────────────────────────────────────────────────
    ML_MODELS_DIR: str = os.getenv(
        "ML_MODELS_DIR",
        str(Path(__file__).parent.parent.parent.parent / "ml" / "models")
    )

    # ── Rate Limiting ─────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()

"""
Structured logging configuration.
Uses JSON format in production for log aggregation tools (Datadog, CloudWatch, etc).
Uses human-readable format in development.
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configure application-wide logging."""

    log_level = logging.DEBUG if settings.is_development() else logging.INFO

    if settings.is_production():
        # JSON structured logging for production log aggregators
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Human-readable for development
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers = [handler]

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    return logging.getLogger("spending_intelligence")

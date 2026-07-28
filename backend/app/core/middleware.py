"""
Request logging middleware.
Logs every API request with method, path, status code, and duration.
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("spending_intelligence.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 1)

        # Skip logging health checks to keep logs clean
        if request.url.path not in ("/health", "/favicon.ico"):
            logger.info(
                "%s %s %s %.1fms",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )

        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response

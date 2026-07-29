import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.database.database import engine, Base

# Import all models so SQLAlchemy registers them before create_all
from app.models.user import User
from app.models.transaction import Transaction
from app.models.automation import Notification, Goal, FinancialHealthScore, JobLog, AIInsight

# Routers
from app.api.auth import router as auth_router
from app.api.sms import router as sms_router
from app.api.transactions import router as transactions_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.ml import router as ml_router
from app.api.automation import router as automation_router
from app.api.download import router as download_router

# Setup logging before anything else
logger = setup_logging()

# Rate limiter — uses client IP
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, start scheduler. Shutdown: stop scheduler."""
    logger.info("Starting AI Spending Intelligence API (env=%s)", settings.ENVIRONMENT)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")

    try:
        from automation.scheduler.scheduler import start_scheduler
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.warning("Scheduler failed to start: %s", e)

    yield

    try:
        from automation.scheduler.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass

    logger.info("API shutdown complete")


app = FastAPI(
    title="AI Spending Intelligence API",
    version="1.0.0",
    description="Personal finance assistant with AI-powered predictions",
    lifespan=lifespan,
    # Hide docs in production
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
)

# ── Middleware (order matters — outermost first) ───────────────────────────

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(sms_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(automation_router)
app.include_router(download_router)


# ── Health check (used by Docker, Nginx, CI/CD) ───────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """
    Returns 200 if the service is running.
    Checks database connectivity.
    """
    from app.database.database import SessionLocal
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        logger.error("Health check DB error: %s", e)
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


# ── Global error handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

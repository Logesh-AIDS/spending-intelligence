import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Allow imports from project root (ml/, automation/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI

from app.database.database import engine, Base

from app.models.user import User
from app.models.transaction import Transaction
from app.models.automation import Notification, Goal, FinancialHealthScore, JobLog, AIInsight

from app.api.auth import router as auth_router
from app.api.sms import router as sms_router
from app.api.transactions import router as transactions_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.ml import router as ml_router
from app.api.automation import router as automation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler on server start, stop on server shutdown."""
    Base.metadata.create_all(bind=engine)

    try:
        from automation.scheduler.scheduler import start_scheduler
        start_scheduler()
        print("✅ Scheduler started")
    except Exception as e:
        print(f"⚠️  Scheduler failed to start: {e}")

    yield  # server is running

    try:
        from automation.scheduler.scheduler import stop_scheduler
        stop_scheduler()
        print("Scheduler stopped")
    except Exception:
        pass


app = FastAPI(
    title="AI Spending Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(sms_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(automation_router)

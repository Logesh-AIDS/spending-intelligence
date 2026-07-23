from fastapi import FastAPI

from app.database.database import engine, Base

# Import all models so SQLAlchemy registers them before create_all
from app.models.user import User
from app.models.transaction import Transaction

# Routers
from app.api.auth import router as auth_router
from app.api.sms import router as sms_router
from app.api.transactions import router as transactions_router
from app.api.dashboard import router as dashboard_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Spending Intelligence API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(sms_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)

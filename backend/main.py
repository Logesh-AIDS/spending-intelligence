from fastapi import FastAPI
from app.api.sms import router as sms_router

app = FastAPI(
    title="AI Spending Intelligence API",
    version="1.0.0"
)

app.include_router(sms_router)
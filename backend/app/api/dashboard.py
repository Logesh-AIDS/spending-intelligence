from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.dashboard import (
    DashboardSummary, TodayDashboard, WeeklyDashboard,
    MonthlyDashboard, BalanceTimeline, SpendingTrend,
)
from app.services import dashboard_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete financial snapshot — totals, averages, recent transactions."""
    return dashboard_service.get_dashboard_summary(db, current_user.id)


@router.get("/today", response_model=TodayDashboard)
def get_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Today's income, expense, balance change and latest transactions."""
    return dashboard_service.get_today_dashboard(db, current_user.id)


@router.get("/weekly", response_model=WeeklyDashboard)
def get_weekly(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Current week's breakdown — daily income/expense, highest spending day."""
    return dashboard_service.get_weekly_dashboard(db, current_user.id)


@router.get("/monthly", response_model=MonthlyDashboard)
def get_monthly(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Monthly dashboard — savings rate, daily trend, largest expense."""
    return dashboard_service.get_monthly_dashboard(db, current_user.id, month, year)


@router.get("/balance-timeline", response_model=BalanceTimeline)
def get_balance_timeline(
    date_from: Optional[str] = Query(None, description="DD/MM/YY"),
    date_to: Optional[str] = Query(None, description="DD/MM/YY"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Balance history for line charts. Optionally filter by date range."""
    return dashboard_service.get_balance_timeline(db, current_user.id, date_from, date_to)


@router.get("/spending-trend", response_model=SpendingTrend)
def get_spending_trend(
    period: str = Query("monthly", description="daily | weekly | monthly | yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregated spending trend — ready for bar/line charts."""
    return dashboard_service.get_spending_trend(db, current_user.id, period)

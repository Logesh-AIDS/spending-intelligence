from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─────────────────────────────────────────────
# Shared
# ─────────────────────────────────────────────

class RecentTransaction(BaseModel):
    id: int
    bank: str
    transaction_type: str
    amount: float
    merchant: Optional[str]
    date: str
    category: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Module 1 – Dashboard Summary
# ─────────────────────────────────────────────

class DashboardSummary(BaseModel):
    current_balance: Optional[float]
    total_spending: float
    total_income: float
    net_cash_flow: float
    savings_percentage: float
    today_spending: float
    this_week_spending: float
    this_month_spending: float
    this_year_spending: float
    total_transactions: int
    debit_count: int
    credit_count: int
    highest_expense: Optional[float]
    highest_income: Optional[float]
    average_transaction: Optional[float]
    average_daily_spending: float
    recent_transactions: List[RecentTransaction]


# ─────────────────────────────────────────────
# Module 2 – Today's Dashboard
# ─────────────────────────────────────────────

class TodayDashboard(BaseModel):
    date: str
    today_income: float
    today_expense: float
    balance_change: float
    transaction_count: int
    largest_transaction: Optional[float]
    latest_transactions: List[RecentTransaction]


# ─────────────────────────────────────────────
# Module 3 – Weekly Dashboard
# ─────────────────────────────────────────────

class DailyBreakdown(BaseModel):
    date: str
    income: float
    expense: float
    net: float
    count: int


class WeeklyDashboard(BaseModel):
    week_start: str
    week_end: str
    weekly_income: float
    weekly_expense: float
    weekly_savings: float
    average_daily_spending: float
    highest_spending_day: Optional[str]
    highest_spending_amount: float
    daily_breakdown: List[DailyBreakdown]


# ─────────────────────────────────────────────
# Module 4 – Monthly Dashboard
# ─────────────────────────────────────────────

class MonthlyDashboard(BaseModel):
    month: str
    year: int
    monthly_income: float
    monthly_expense: float
    monthly_savings: float
    savings_rate: float
    average_daily_spending: float
    largest_expense: Optional[float]
    transaction_count: int
    daily_spending_trend: List[DailyBreakdown]


# ─────────────────────────────────────────────
# Module 5 – Balance Timeline
# ─────────────────────────────────────────────

class BalancePoint(BaseModel):
    date: str
    balance: float


class BalanceTimeline(BaseModel):
    timeline: List[BalancePoint]


# ─────────────────────────────────────────────
# Module 6 – Spending Trend
# ─────────────────────────────────────────────

class TrendPoint(BaseModel):
    label: str
    amount: float
    count: int


class SpendingTrend(BaseModel):
    period: str           # "daily" | "weekly" | "monthly" | "yearly"
    data: List[TrendPoint]

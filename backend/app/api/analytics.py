from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.analytics import (
    MerchantAnalytics, CategoryAnalytics, IncomeVsExpense,
    SpendingBehaviour, FinancialStatistics, Report,
)
from app.services import analytics_service
from app.services import transaction_service
from app.schemas.transaction import PaginatedTransactions

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/merchants", response_model=MerchantAnalytics)
def get_merchant_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Merchant-wise spending, top merchants, frequency."""
    return analytics_service.get_merchant_analytics(db, current_user.id)


@router.get("/categories", response_model=CategoryAnalytics)
def get_category_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Category breakdown with percentages and highest spending category."""
    return analytics_service.get_category_analytics(db, current_user.id)


@router.get("/income-vs-expense", response_model=IncomeVsExpense)
def get_income_vs_expense(
    period: str = Query("monthly", description="daily | weekly | monthly | yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Income vs expense breakdown by period with savings rate."""
    return analytics_service.get_income_vs_expense(db, current_user.id, period)


@router.get("/behaviour", response_model=SpendingBehaviour)
def get_spending_behaviour(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Spending behaviour: average, median, std deviation, weekend vs weekday."""
    return analytics_service.get_spending_behaviour(db, current_user.id)


@router.get("/statistics", response_model=FinancialStatistics)
def get_financial_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete financial statistics for the authenticated user."""
    return analytics_service.get_financial_statistics(db, current_user.id)


@router.get("/search", response_model=PaginatedTransactions)
def search_transactions(
    # search filters
    merchant: Optional[str] = None,
    bank: Optional[str] = None,
    upi_reference: Optional[str] = None,
    account_number: Optional[str] = None,
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = Query(None, description="DD/MM/YY"),
    date_to: Optional[str] = Query(None, description="DD/MM/YY"),
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = Query(None, description="Fuzzy search across merchant, bank, UPI"),
    # pagination
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search transactions with multiple filters.
    Supports combining merchant, date range, amount range, type, category, UPI, fuzzy search.
    """
    return transaction_service.get_transactions(
        db=db, user_id=current_user.id,
        page=page, page_size=page_size,
        transaction_type=transaction_type,
        merchant=merchant, bank=bank, category=category,
        date_from=date_from, date_to=date_to,
        min_amount=min_amount, max_amount=max_amount,
        search=search or upi_reference or account_number,
        sort_by=sort_by, sort_order=sort_order,
    )


@router.get("/report", response_model=Report)
def get_report(
    report_type: str = Query("monthly", description="weekly | monthly | yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate financial report grouped by period.
    Returns income, expense, savings, top merchant and category per period.
    """
    return analytics_service.get_report(db, current_user.id, report_type)

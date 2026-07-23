from pydantic import BaseModel
from typing import Optional, List, Dict


# ─────────────────────────────────────────────
# Module 7 – Merchant Analytics
# ─────────────────────────────────────────────

class MerchantStat(BaseModel):
    merchant: str
    total_spent: float
    transaction_count: int
    percentage: float
    average_amount: float


class MerchantAnalytics(BaseModel):
    total_merchants: int
    favorite_merchant: Optional[str]
    merchants: List[MerchantStat]


# ─────────────────────────────────────────────
# Module 8 – Category Analytics
# ─────────────────────────────────────────────

class CategoryStat(BaseModel):
    category: str
    total_spent: float
    transaction_count: int
    percentage: float


class CategoryAnalytics(BaseModel):
    total_categories: int
    highest_spending_category: Optional[str]
    categories: List[CategoryStat]


# ─────────────────────────────────────────────
# Module 9 – Income vs Expense
# ─────────────────────────────────────────────

class IncomeExpensePoint(BaseModel):
    label: str
    income: float
    expense: float
    savings: float
    savings_rate: float


class IncomeVsExpense(BaseModel):
    period: str
    total_income: float
    total_expense: float
    total_savings: float
    overall_savings_rate: float
    data: List[IncomeExpensePoint]


# ─────────────────────────────────────────────
# Module 10 – Spending Behaviour
# ─────────────────────────────────────────────

class SpendingBehaviour(BaseModel):
    average_spending: float
    median_spending: float
    max_spending: float
    min_spending: float
    std_deviation: float
    transaction_frequency_per_day: float
    weekend_spending: float
    weekday_spending: float
    weekend_vs_weekday_ratio: float
    most_active_day: Optional[str]


# ─────────────────────────────────────────────
# Module 11 – Financial Statistics
# ─────────────────────────────────────────────

class FinancialStatistics(BaseModel):
    total_transactions: int
    total_debit_transactions: int
    total_credit_transactions: int
    total_debit_amount: float
    total_credit_amount: float
    average_debit_amount: float
    average_credit_amount: float
    highest_debit: Optional[float]
    highest_credit: Optional[float]
    lowest_debit: Optional[float]
    lowest_credit: Optional[float]
    std_deviation_spending: float


# ─────────────────────────────────────────────
# Module 13 – Reports
# ─────────────────────────────────────────────

class ReportEntry(BaseModel):
    label: str
    income: float
    expense: float
    savings: float
    transaction_count: int
    top_merchant: Optional[str]
    top_category: Optional[str]


class Report(BaseModel):
    report_type: str
    generated_at: str
    total_income: float
    total_expense: float
    total_savings: float
    entries: List[ReportEntry]

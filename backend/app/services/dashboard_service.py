from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction


def get_dashboard_summary(db: Session, user_id: int) -> dict:

    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())       # Monday
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Dates are stored as "DD/MM/YY" strings from Canara SMS parser
    # Format helpers for comparison
    def fmt(d):
        return d.strftime("%d/%m/%y")

    today_str = fmt(today)
    week_start_str = fmt(week_start)
    month_start_str = fmt(month_start)
    year_start_str = fmt(year_start)

    # ------------------------------------------------------------------
    # Base query scoped to this user
    # ------------------------------------------------------------------
    base = db.query(Transaction).filter(Transaction.user_id == user_id)

    # ------------------------------------------------------------------
    # Totals
    # ------------------------------------------------------------------
    total_spending = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).scalar() or 0.0

    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Credit"
    ).scalar() or 0.0

    # ------------------------------------------------------------------
    # Period spending  (date string comparison works for same DD/MM/YY format)
    # ------------------------------------------------------------------
    def period_spending(from_str):
        return db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Debit",
            Transaction.date >= from_str
        ).scalar() or 0.0

    today_spending = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit",
        Transaction.date == today_str
    ).scalar() or 0.0

    this_week_spending = period_spending(week_start_str)
    this_month_spending = period_spending(month_start_str)
    this_year_spending = period_spending(year_start_str)

    # ------------------------------------------------------------------
    # Transaction counts
    # ------------------------------------------------------------------
    total_transactions = base.count()

    debit_count = base.filter(Transaction.transaction_type == "Debit").count()
    credit_count = base.filter(Transaction.transaction_type == "Credit").count()

    # ------------------------------------------------------------------
    # Extremes and averages (debits only — spending analysis)
    # ------------------------------------------------------------------
    debit_base = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    )

    highest_transaction = db.query(func.max(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).scalar()

    lowest_transaction = db.query(func.min(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).scalar()

    average_transaction = db.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).scalar()

    # ------------------------------------------------------------------
    # Average daily and monthly spending
    # Days since first transaction
    # ------------------------------------------------------------------
    first_txn = base.order_by(Transaction.created_at.asc()).first()

    if first_txn and total_spending > 0:
        days_active = max((datetime.utcnow() - first_txn.created_at).days, 1)
        average_daily_spending = total_spending / days_active
        months_active = max(days_active / 30, 1)
        average_monthly_spending = total_spending / months_active
    else:
        average_daily_spending = 0.0
        average_monthly_spending = 0.0

    # ------------------------------------------------------------------
    # Current balance — most recent transaction's balance field
    # ------------------------------------------------------------------
    latest_txn = base.filter(
        Transaction.balance.isnot(None)
    ).order_by(Transaction.created_at.desc()).first()

    current_balance = latest_txn.balance if latest_txn else None

    # ------------------------------------------------------------------
    # Recent 5 transactions
    # ------------------------------------------------------------------
    recent = base.order_by(Transaction.created_at.desc()).limit(5).all()

    return {
        "current_balance": current_balance,
        "total_spending": round(total_spending, 2),
        "total_income": round(total_income, 2),
        "net_cash_flow": round(total_income - total_spending, 2),
        "today_spending": round(today_spending, 2),
        "this_week_spending": round(this_week_spending, 2),
        "this_month_spending": round(this_month_spending, 2),
        "this_year_spending": round(this_year_spending, 2),
        "total_transactions": total_transactions,
        "debit_count": debit_count,
        "credit_count": credit_count,
        "highest_transaction": round(highest_transaction, 2) if highest_transaction else None,
        "lowest_transaction": round(lowest_transaction, 2) if lowest_transaction else None,
        "average_transaction": round(average_transaction, 2) if average_transaction else None,
        "average_daily_spending": round(average_daily_spending, 2),
        "average_monthly_spending": round(average_monthly_spending, 2),
        "recent_transactions": recent,
    }

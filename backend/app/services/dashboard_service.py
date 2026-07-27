from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction


# ─────────────────────────────────────────────
# Date utilities
# ─────────────────────────────────────────────

def _fmt(d) -> str:
    """Convert date to DD/MM/YY string — matches how SMS parser stores dates."""
    return d.strftime("%d/%m/%y")


def _parse_date(date_str: str):
    """Parse DD/MM/YY string back to date object. Returns None on failure."""
    try:
        return datetime.strptime(date_str, "%d/%m/%y").date()
    except Exception:
        return None


def _today_bounds():
    today = datetime.utcnow().date()
    return today, _fmt(today)


# ─────────────────────────────────────────────
# Module 1 – Dashboard Summary
# ─────────────────────────────────────────────

def get_dashboard_summary(db: Session, user_id: int) -> dict:
    today, today_str = _today_bounds()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    base = db.query(Transaction).filter(Transaction.user_id == user_id)

    total_spending = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).scalar() or 0.0

    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Credit"
    ).scalar() or 0.0

    savings_percentage = round((total_income - total_spending) / total_income * 100, 2) if total_income > 0 else 0.0

    today_spending = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit",
        Transaction.date == today_str
    ).scalar() or 0.0

    def period_spending(from_date):
        return db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Debit",
            Transaction.date >= _fmt(from_date)
        ).scalar() or 0.0

    total_transactions = base.count()
    debit_count = base.filter(Transaction.transaction_type == "Debit").count()
    credit_count = base.filter(Transaction.transaction_type == "Credit").count()

    highest_expense = db.query(func.max(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.transaction_type == "Debit"
    ).scalar()

    highest_income = db.query(func.max(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.transaction_type == "Credit"
    ).scalar()

    avg_txn = db.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.transaction_type == "Debit"
    ).scalar()

    first_txn = base.order_by(Transaction.created_at.asc()).first()
    days_active = max((datetime.utcnow() - first_txn.created_at).days, 1) if first_txn else 1
    avg_daily = round(total_spending / days_active, 2) if total_spending > 0 else 0.0

    latest_with_balance = base.filter(Transaction.balance.isnot(None)).order_by(
        Transaction.created_at.desc()
    ).first()

    recent = base.order_by(Transaction.created_at.desc()).limit(5).all()

    return {
        "current_balance": latest_with_balance.balance if latest_with_balance else None,
        "total_spending": round(total_spending, 2),
        "total_income": round(total_income, 2),
        "net_cash_flow": round(total_income - total_spending, 2),
        "savings_percentage": savings_percentage,
        "today_spending": round(today_spending, 2),
        "this_week_spending": round(period_spending(week_start), 2),
        "this_month_spending": round(period_spending(month_start), 2),
        "this_year_spending": round(period_spending(year_start), 2),
        "total_transactions": total_transactions,
        "debit_count": debit_count,
        "credit_count": credit_count,
        "highest_expense": round(highest_expense, 2) if highest_expense else None,
        "highest_income": round(highest_income, 2) if highest_income else None,
        "average_transaction": round(avg_txn, 2) if avg_txn else None,
        "average_daily_spending": avg_daily,
        "recent_transactions": recent,
    }


# ─────────────────────────────────────────────
# Module 2 – Today's Dashboard
# ─────────────────────────────────────────────

def get_today_dashboard(db: Session, user_id: int) -> dict:
    today, today_str = _today_bounds()

    today_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date == today_str
    ).order_by(Transaction.created_at.desc()).all()

    income = sum(t.amount for t in today_txns if t.transaction_type == "Credit")
    expense = sum(t.amount for t in today_txns if t.transaction_type == "Debit")
    largest = max((t.amount for t in today_txns), default=None)

    return {
        "date": today_str,
        "today_income": round(income, 2),
        "today_expense": round(expense, 2),
        "balance_change": round(income - expense, 2),
        "transaction_count": len(today_txns),
        "largest_transaction": round(largest, 2) if largest else None,
        "latest_transactions": today_txns[:5],
    }


# ─────────────────────────────────────────────
# Module 3 – Weekly Dashboard
# ─────────────────────────────────────────────

def get_weekly_dashboard(db: Session, user_id: int) -> dict:
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)             # Sunday

    # Fetch all transactions for the week
    all_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= _fmt(week_start),
        Transaction.date <= _fmt(week_end)
    ).all()

    # Build daily breakdown
    daily: dict = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = _fmt(day)
        daily[day_str] = {"date": day_str, "income": 0.0, "expense": 0.0, "net": 0.0, "count": 0}

    for t in all_txns:
        if t.date in daily:
            if t.transaction_type == "Credit":
                daily[t.date]["income"] += t.amount
            else:
                daily[t.date]["expense"] += t.amount
            daily[t.date]["count"] += 1

    for d in daily.values():
        d["net"] = round(d["income"] - d["expense"], 2)
        d["income"] = round(d["income"], 2)
        d["expense"] = round(d["expense"], 2)

    daily_list = list(daily.values())

    weekly_income = sum(d["income"] for d in daily_list)
    weekly_expense = sum(d["expense"] for d in daily_list)
    avg_daily = round(weekly_expense / 7, 2)

    highest_day = max(daily_list, key=lambda x: x["expense"], default=None)

    return {
        "week_start": _fmt(week_start),
        "week_end": _fmt(week_end),
        "weekly_income": round(weekly_income, 2),
        "weekly_expense": round(weekly_expense, 2),
        "weekly_savings": round(weekly_income - weekly_expense, 2),
        "average_daily_spending": avg_daily,
        "highest_spending_day": highest_day["date"] if highest_day else None,
        "highest_spending_amount": highest_day["expense"] if highest_day else 0.0,
        "daily_breakdown": daily_list,
    }


# ─────────────────────────────────────────────
# Module 4 – Monthly Dashboard
# ─────────────────────────────────────────────

def get_monthly_dashboard(db: Session, user_id: int, month: int = None, year: int = None) -> dict:
    today = datetime.utcnow().date()
    month = month or today.month
    year = year or today.year

    import calendar
    _, days_in_month = calendar.monthrange(year, month)
    month_start = today.replace(year=year, month=month, day=1)
    month_end = today.replace(year=year, month=month, day=days_in_month)

    all_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= _fmt(month_start),
        Transaction.date <= _fmt(month_end)
    ).all()

    daily: dict = {}
    for i in range(days_in_month):
        day = month_start + timedelta(days=i)
        day_str = _fmt(day)
        daily[day_str] = {"date": day_str, "income": 0.0, "expense": 0.0, "net": 0.0, "count": 0}

    for t in all_txns:
        if t.date in daily:
            if t.transaction_type == "Credit":
                daily[t.date]["income"] += t.amount
            else:
                daily[t.date]["expense"] += t.amount
            daily[t.date]["count"] += 1

    for d in daily.values():
        d["net"] = round(d["income"] - d["expense"], 2)
        d["income"] = round(d["income"], 2)
        d["expense"] = round(d["expense"], 2)

    daily_list = list(daily.values())
    monthly_income = sum(d["income"] for d in daily_list)
    monthly_expense = sum(d["expense"] for d in daily_list)
    monthly_savings = monthly_income - monthly_expense
    savings_rate = round(monthly_savings / monthly_income * 100, 2) if monthly_income > 0 else 0.0
    avg_daily = round(monthly_expense / days_in_month, 2)
    largest = max((t.amount for t in all_txns if t.transaction_type == "Debit"), default=None)

    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    return {
        "month": month_names[month],
        "year": year,
        "monthly_income": round(monthly_income, 2),
        "monthly_expense": round(monthly_expense, 2),
        "monthly_savings": round(monthly_savings, 2),
        "savings_rate": savings_rate,
        "average_daily_spending": avg_daily,
        "largest_expense": round(largest, 2) if largest else None,
        "transaction_count": len(all_txns),
        "daily_spending_trend": daily_list,
    }


# ─────────────────────────────────────────────
# Module 5 – Balance Timeline
# ─────────────────────────────────────────────

def get_balance_timeline(db: Session, user_id: int, date_from: str = None, date_to: str = None) -> dict:
    """
    Returns all transactions that have a balance field, ordered by date.
    Frontend uses this to draw balance line charts.
    """
    q = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.balance.isnot(None)
    )
    if date_from:
        q = q.filter(Transaction.date >= date_from)
    if date_to:
        q = q.filter(Transaction.date <= date_to)

    txns = q.order_by(Transaction.created_at.asc()).all()

    timeline = [{"date": t.date, "balance": t.balance} for t in txns]

    return {"timeline": timeline}


# ─────────────────────────────────────────────
# Module 6 – Spending Trend
# ─────────────────────────────────────────────

def get_spending_trend(db: Session, user_id: int, period: str = "monthly") -> dict:
    """
    period: "daily" | "weekly" | "monthly" | "yearly"
    Returns aggregated spending data ready for chart libraries.
    """
    debits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).all()

    buckets: dict = defaultdict(lambda: {"amount": 0.0, "count": 0})

    for t in debits:
        d = _parse_date(t.date)
        if not d:
            continue

        if period == "daily":
            label = _fmt(d)
        elif period == "weekly":
            # ISO week label e.g. "2026-W29"
            label = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
        elif period == "monthly":
            label = d.strftime("%b %Y")  # e.g. "Jul 2026"
        elif period == "yearly":
            label = str(d.year)
        else:
            label = _fmt(d)

        buckets[label]["amount"] += t.amount
        buckets[label]["count"] += 1

    data = [
        {"label": k, "amount": round(v["amount"], 2), "count": v["count"]}
        for k, v in sorted(buckets.items())
    ]

    return {"period": period, "data": data}

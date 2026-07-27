from datetime import datetime, timedelta
from collections import defaultdict
from statistics import median, stdev
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%d/%m/%y").date()
    except Exception:
        return None


def _fmt(d) -> str:
    return d.strftime("%d/%m/%y")


# ─────────────────────────────────────────────
# Module 7 – Merchant Analytics
# ─────────────────────────────────────────────

def get_merchant_analytics(db: Session, user_id: int) -> dict:
    debits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit",
        Transaction.merchant.isnot(None)
    ).all()

    total_spent = sum(t.amount for t in debits) or 1.0  # avoid division by zero

    merchant_map: dict = defaultdict(lambda: {"total": 0.0, "count": 0})
    for t in debits:
        merchant_map[t.merchant]["total"] += t.amount
        merchant_map[t.merchant]["count"] += 1

    merchants = [
        {
            "merchant": m,
            "total_spent": round(v["total"], 2),
            "transaction_count": v["count"],
            "percentage": round(v["total"] / total_spent * 100, 2),
            "average_amount": round(v["total"] / v["count"], 2),
        }
        for m, v in merchant_map.items()
    ]
    merchants.sort(key=lambda x: x["total_spent"], reverse=True)

    favorite = merchants[0]["merchant"] if merchants else None

    return {
        "total_merchants": len(merchants),
        "favorite_merchant": favorite,
        "merchants": merchants,
    }


# ─────────────────────────────────────────────
# Module 8 – Category Analytics
# ─────────────────────────────────────────────

def get_category_analytics(db: Session, user_id: int) -> dict:
    debits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).all()

    total_spent = sum(t.amount for t in debits) or 1.0

    cat_map: dict = defaultdict(lambda: {"total": 0.0, "count": 0})
    for t in debits:
        cat = t.category or "Others"
        cat_map[cat]["total"] += t.amount
        cat_map[cat]["count"] += 1

    categories = [
        {
            "category": c,
            "total_spent": round(v["total"], 2),
            "transaction_count": v["count"],
            "percentage": round(v["total"] / total_spent * 100, 2),
        }
        for c, v in cat_map.items()
    ]
    categories.sort(key=lambda x: x["total_spent"], reverse=True)

    highest = categories[0]["category"] if categories else None

    return {
        "total_categories": len(categories),
        "highest_spending_category": highest,
        "categories": categories,
    }


# ─────────────────────────────────────────────
# Module 9 – Income vs Expense
# ─────────────────────────────────────────────

def get_income_vs_expense(db: Session, user_id: int, period: str = "monthly") -> dict:
    all_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).all()

    buckets: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

    for t in all_txns:
        d = _parse_date(t.date)
        if not d:
            continue

        if period == "daily":
            label = _fmt(d)
        elif period == "weekly":
            label = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
        elif period == "monthly":
            label = d.strftime("%b %Y")
        elif period == "yearly":
            label = str(d.year)
        else:
            label = d.strftime("%b %Y")

        if t.transaction_type == "Credit":
            buckets[label]["income"] += t.amount
        else:
            buckets[label]["expense"] += t.amount

    data = []
    for label in sorted(buckets.keys()):
        v = buckets[label]
        savings = v["income"] - v["expense"]
        rate = round(savings / v["income"] * 100, 2) if v["income"] > 0 else 0.0
        data.append({
            "label": label,
            "income": round(v["income"], 2),
            "expense": round(v["expense"], 2),
            "savings": round(savings, 2),
            "savings_rate": rate,
        })

    total_income = sum(d["income"] for d in data)
    total_expense = sum(d["expense"] for d in data)
    total_savings = total_income - total_expense
    overall_rate = round(total_savings / total_income * 100, 2) if total_income > 0 else 0.0

    return {
        "period": period,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_savings": round(total_savings, 2),
        "overall_savings_rate": overall_rate,
        "data": data,
    }


# ─────────────────────────────────────────────
# Module 10 – Spending Behaviour
# ─────────────────────────────────────────────

def get_spending_behaviour(db: Session, user_id: int) -> dict:
    debits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).all()

    amounts = [t.amount for t in debits]

    if not amounts:
        return {
            "average_spending": 0.0, "median_spending": 0.0,
            "max_spending": 0.0, "min_spending": 0.0,
            "std_deviation": 0.0, "transaction_frequency_per_day": 0.0,
            "weekend_spending": 0.0, "weekday_spending": 0.0,
            "weekend_vs_weekday_ratio": 0.0, "most_active_day": None,
        }

    avg = round(sum(amounts) / len(amounts), 2)
    med = round(median(amounts), 2)
    std = round(stdev(amounts), 2) if len(amounts) > 1 else 0.0

    # Weekend vs weekday
    weekend_total = 0.0
    weekday_total = 0.0
    day_counts: dict = defaultdict(float)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for t in debits:
        d = _parse_date(t.date)
        if not d:
            continue
        weekday = d.weekday()
        day_counts[day_names[weekday]] += t.amount
        if weekday >= 5:
            weekend_total += t.amount
        else:
            weekday_total += t.amount

    ratio = round(weekend_total / weekday_total, 2) if weekday_total > 0 else 0.0
    most_active = max(day_counts, key=day_counts.get) if day_counts else None

    # Transaction frequency — transactions per day since first transaction
    first = min((_parse_date(t.date) for t in debits if _parse_date(t.date)), default=None)
    last = max((_parse_date(t.date) for t in debits if _parse_date(t.date)), default=None)
    days_range = max((last - first).days, 1) if first and last else 1
    freq = round(len(debits) / days_range, 2)

    return {
        "average_spending": avg,
        "median_spending": med,
        "max_spending": round(max(amounts), 2),
        "min_spending": round(min(amounts), 2),
        "std_deviation": std,
        "transaction_frequency_per_day": freq,
        "weekend_spending": round(weekend_total, 2),
        "weekday_spending": round(weekday_total, 2),
        "weekend_vs_weekday_ratio": ratio,
        "most_active_day": most_active,
    }


# ─────────────────────────────────────────────
# Module 11 – Financial Statistics
# ─────────────────────────────────────────────

def get_financial_statistics(db: Session, user_id: int) -> dict:
    debits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Debit"
    ).all()

    credits = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "Credit"
    ).all()

    debit_amounts = [t.amount for t in debits]
    credit_amounts = [t.amount for t in credits]

    total = len(debits) + len(credits)
    total_debit = sum(debit_amounts)
    total_credit = sum(credit_amounts)
    avg_debit = round(total_debit / len(debit_amounts), 2) if debit_amounts else 0.0
    avg_credit = round(total_credit / len(credit_amounts), 2) if credit_amounts else 0.0
    std = round(stdev(debit_amounts), 2) if len(debit_amounts) > 1 else 0.0

    return {
        "total_transactions": total,
        "total_debit_transactions": len(debits),
        "total_credit_transactions": len(credits),
        "total_debit_amount": round(total_debit, 2),
        "total_credit_amount": round(total_credit, 2),
        "average_debit_amount": avg_debit,
        "average_credit_amount": avg_credit,
        "highest_debit": round(max(debit_amounts), 2) if debit_amounts else None,
        "highest_credit": round(max(credit_amounts), 2) if credit_amounts else None,
        "lowest_debit": round(min(debit_amounts), 2) if debit_amounts else None,
        "lowest_credit": round(min(credit_amounts), 2) if credit_amounts else None,
        "std_deviation_spending": std,
    }


# ─────────────────────────────────────────────
# Module 13 – Reports
# ─────────────────────────────────────────────

def get_report(db: Session, user_id: int, report_type: str = "monthly") -> dict:
    """
    report_type: "weekly" | "monthly" | "yearly"
    Returns grouped data ready for frontend report rendering.
    """
    all_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).all()

    buckets: dict = defaultdict(lambda: {
        "income": 0.0, "expense": 0.0, "count": 0,
        "merchants": defaultdict(float), "categories": defaultdict(float)
    })

    for t in all_txns:
        d = _parse_date(t.date)
        if not d:
            continue

        if report_type == "weekly":
            label = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
        elif report_type == "yearly":
            label = str(d.year)
        else:
            label = d.strftime("%b %Y")

        if t.transaction_type == "Credit":
            buckets[label]["income"] += t.amount
        else:
            buckets[label]["expense"] += t.amount
            if t.merchant:
                buckets[label]["merchants"][t.merchant] += t.amount
            if t.category:
                buckets[label]["categories"][t.category] += t.amount

        buckets[label]["count"] += 1

    entries = []
    for label in sorted(buckets.keys()):
        v = buckets[label]
        top_merchant = max(v["merchants"], key=v["merchants"].get) if v["merchants"] else None
        top_category = max(v["categories"], key=v["categories"].get) if v["categories"] else None
        savings = v["income"] - v["expense"]
        entries.append({
            "label": label,
            "income": round(v["income"], 2),
            "expense": round(v["expense"], 2),
            "savings": round(savings, 2),
            "transaction_count": v["count"],
            "top_merchant": top_merchant,
            "top_category": top_category,
        })

    total_income = sum(e["income"] for e in entries)
    total_expense = sum(e["expense"] for e in entries)

    return {
        "report_type": report_type,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_savings": round(total_income - total_expense, 2),
        "entries": entries,
    }

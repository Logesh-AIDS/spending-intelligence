"""
Module 8 – Financial Health Score
Composite AI-generated score (0-100) from multiple financial dimensions.

Weights:
  Savings Rate        25%   — are you saving money?
  Expense Ratio       20%   — how much of income goes to expenses?
  Cash Flow           20%   — is money coming in or going out?
  Spending Trend      15%   — is spending increasing or decreasing?
  Consistency         10%   — regular income, stable behaviour?
  Budget Adherence    10%   — staying within normal patterns?
"""
import json
from typing import Dict, Any


WEIGHTS = {
    "savings": 0.25,
    "expense": 0.20,
    "cash_flow": 0.20,
    "trend": 0.15,
    "consistency": 0.10,
    "budget": 0.10,
}


def _score_savings(savings_rate: float) -> float:
    """0-100. Saving 30%+ = 100. Saving 0% = 0. Negative = 0."""
    if savings_rate >= 0.30:
        return 100.0
    elif savings_rate >= 0.20:
        return 80.0
    elif savings_rate >= 0.10:
        return 60.0
    elif savings_rate >= 0.05:
        return 40.0
    elif savings_rate >= 0:
        return 20.0
    else:
        return 0.0  # spending more than earning


def _score_expense(expense_ratio: float) -> float:
    """Lower expense ratio = better. 0-100."""
    if expense_ratio <= 0.50:
        return 100.0
    elif expense_ratio <= 0.70:
        return 80.0
    elif expense_ratio <= 0.85:
        return 60.0
    elif expense_ratio <= 1.0:
        return 40.0
    else:
        return 0.0  # expenses > income


def _score_cash_flow(net_cash_flow: float, total_income: float) -> float:
    """Positive cash flow scores higher."""
    if total_income <= 0:
        return 50.0
    ratio = net_cash_flow / total_income
    if ratio >= 0.30:
        return 100.0
    elif ratio >= 0.10:
        return 80.0
    elif ratio >= 0:
        return 60.0
    elif ratio >= -0.10:
        return 30.0
    else:
        return 0.0


def _score_trend(this_month: float, avg_monthly: float) -> float:
    """Is spending getting better or worse?"""
    if avg_monthly <= 0:
        return 50.0
    ratio = this_month / avg_monthly
    if ratio <= 0.8:
        return 100.0   # spending less than usual — great
    elif ratio <= 1.0:
        return 80.0
    elif ratio <= 1.2:
        return 60.0
    elif ratio <= 1.5:
        return 40.0
    else:
        return 20.0    # spending much more than usual


def _score_consistency(total_transactions: int, debit_count: int) -> float:
    """Regular transaction activity signals financial stability."""
    if total_transactions >= 20:
        return 100.0
    elif total_transactions >= 10:
        return 80.0
    elif total_transactions >= 5:
        return 60.0
    else:
        return 40.0


def _score_budget(avg_daily: float, today: float) -> float:
    """Is today's spending within normal daily bounds?"""
    if avg_daily <= 0:
        return 70.0
    ratio = today / avg_daily if avg_daily > 0 else 1.0
    if ratio <= 1.0:
        return 100.0
    elif ratio <= 1.5:
        return 70.0
    elif ratio <= 2.0:
        return 40.0
    else:
        return 10.0


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "F"


def _interpretation(score: float, grade: str) -> str:
    messages = {
        "A": "Excellent financial health. You are saving consistently and managing expenses well.",
        "B": "Good financial health. Minor improvements in savings or consistency could push you higher.",
        "C": "Average financial health. Consider reviewing your largest expense categories.",
        "D": "Below average. Your expenses are too high relative to income. Immediate action recommended.",
        "F": "Critical financial health. Expenses exceed income. Urgent budget review required.",
    }
    return messages[grade]


def _improvement_tips(components: Dict) -> list:
    tips = []
    if components["savings"] < 60:
        tips.append("Increase your savings rate to at least 20% of income.")
    if components["expense"] < 60:
        tips.append("Reduce monthly expenses — identify and cut top 2 spending categories.")
    if components["cash_flow"] < 60:
        tips.append("Improve cash flow by reducing discretionary spending this month.")
    if components["trend"] < 60:
        tips.append("Your spending is rising. Set a weekly spending limit.")
    if components["budget"] < 60:
        tips.append("Today's spending is above your daily average. Avoid non-essential purchases.")
    if not tips:
        tips.append("Keep up the good habits. Consider investing your savings for long-term growth.")
    return tips


def calculate_health_score(stats: Dict[str, Any]) -> Dict:
    """
    Calculate the financial health score from dashboard stats.
    
    Args:
        stats: output of dashboard_service.get_dashboard_summary()
    
    Returns:
        Score dict with grade, components, interpretation, tips
    """
    savings_rate = stats.get("savings_percentage", 0) / 100
    total_income = stats.get("total_income", 0)
    total_spending = stats.get("total_spending", 0)
    expense_ratio = total_spending / total_income if total_income > 0 else 1.0
    net_cash_flow = stats.get("net_cash_flow", 0)
    this_month = stats.get("this_month_spending", 0)
    avg_monthly = stats.get("average_monthly_spending", 0) or 1.0
    total_transactions = stats.get("total_transactions", 0)
    debit_count = stats.get("debit_count", 0)
    avg_daily = stats.get("average_daily_spending", 0) or 1.0
    today = stats.get("today_spending", 0)

    components = {
        "savings": _score_savings(savings_rate),
        "expense": _score_expense(expense_ratio),
        "cash_flow": _score_cash_flow(net_cash_flow, total_income),
        "trend": _score_trend(this_month, avg_monthly),
        "consistency": _score_consistency(total_transactions, debit_count),
        "budget": _score_budget(avg_daily, today),
    }

    # Weighted composite score
    score = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
    score = round(score, 1)
    grade = _grade(score)

    return {
        "score": score,
        "grade": grade,
        "savings_component": components["savings"],
        "expense_component": components["expense"],
        "cash_flow_component": components["cash_flow"],
        "trend_component": components["trend"],
        "consistency_component": components["consistency"],
        "budget_component": components["budget"],
        "interpretation": _interpretation(score, grade),
        "improvement_tips": _improvement_tips(components),
    }

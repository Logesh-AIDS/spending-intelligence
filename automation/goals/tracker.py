"""
Module 7 – Goal Tracking
Evaluates user goals against real transaction data and predicts achievement.
"""
from datetime import datetime
from typing import Dict, Any


def evaluate_goal(goal: Dict, user_stats: Dict) -> Dict:
    """
    Evaluate a single goal and return progress + AI prediction.
    
    Args:
        goal: Goal model dict
        user_stats: dashboard summary
    
    Returns:
        Updated goal progress dict
    """
    goal_type = goal.get("goal_type")
    target = goal.get("target_amount", 0)
    category = goal.get("category")

    current = 0.0

    if goal_type == "save":
        # Progress = net cash flow so far this month
        current = max(user_stats.get("net_cash_flow", 0), 0)

    elif goal_type == "limit_category":
        # Progress = how much of limit has been used in this month's category spend
        # We use total spending as proxy (full category breakdown from analytics needed)
        current = user_stats.get("this_month_spending", 0)

    elif goal_type == "emergency_fund":
        # Progress = current balance vs target
        current = user_stats.get("current_balance") or 0.0

    elif goal_type == "limit_spending":
        current = user_stats.get("this_month_spending", 0)

    # Progress percentage
    if target > 0:
        progress = (current / target) * 100
        if goal_type in ("save", "emergency_fund"):
            progress = min(progress, 100.0)  # capped at 100 for savings goals
        else:
            # For limit goals: 100% = limit reached, >100% = exceeded
            pass
    else:
        progress = 0.0

    # AI prediction
    deadline_str = goal.get("deadline")
    days_remaining = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%d/%m/%y")
            days_remaining = (deadline - datetime.utcnow()).days
        except Exception:
            pass

    prediction = _predict_goal_outcome(goal_type, progress, days_remaining, user_stats)
    is_achieved = progress >= 100.0 if goal_type in ("save", "emergency_fund") else False

    return {
        "current_amount": round(current, 2),
        "progress_percentage": round(progress, 1),
        "ai_prediction": prediction,
        "is_achieved": is_achieved,
        "days_remaining": days_remaining,
    }


def _predict_goal_outcome(goal_type: str, progress: float, days_remaining, stats: Dict) -> str:
    """Predict whether the goal will be achieved."""
    if progress >= 100:
        return "achieved"

    if days_remaining is None:
        return "on_track" if progress >= 50 else "at_risk"

    if days_remaining <= 0:
        return "failed" if progress < 100 else "achieved"

    # Extrapolate: if current progress continues at same rate, will goal be met?
    total_days = max(days_remaining, 1)

    if goal_type == "save":
        avg_daily_saving = stats.get("average_daily_spending", 0)
        savings_rate = stats.get("savings_percentage", 0) / 100
        # Rough projection
        if savings_rate > 0.15:
            return "on_track"
        elif savings_rate > 0.05:
            return "at_risk"
        else:
            return "failed"

    elif goal_type in ("limit_category", "limit_spending"):
        # If spending exceeds limit — fail
        if progress > 100:
            return "failed"
        elif progress > 80 and days_remaining > 10:
            return "at_risk"
        else:
            return "on_track"

    return "on_track" if progress >= (100 - days_remaining * 2) else "at_risk"

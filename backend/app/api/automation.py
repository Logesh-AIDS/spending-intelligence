"""
Phase 8 – Automation APIs
Notifications, goals, health score, insights, job admin.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.models.automation import Notification, Goal, FinancialHealthScore, AIInsight, JobLog
from app.core.dependencies import get_current_user
from app.schemas.automation import (
    NotificationResponse, GoalCreate, GoalResponse,
    HealthScoreResponse, InsightResponse, JobLogResponse,
)
from app.services.dashboard_service import get_dashboard_summary
from app.services.analytics_service import get_merchant_analytics, get_spending_behaviour

router = APIRouter(prefix="/api/v1", tags=["Automation"])


# ─────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notifications for the authenticated user."""
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    return q.order_by(Notification.created_at.desc()).limit(limit).all()


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    note = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.post("/notifications/generate")
def generate_notifications_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger notification generation for the current user."""
    from automation.notifications.engine import generate_notifications

    stats = get_dashboard_summary(db, current_user.id)
    notes = generate_notifications(user_stats=stats)

    created = 0
    for n in notes:
        note = Notification(
            user_id=current_user.id,
            title=n["title"],
            message=n["message"],
            notification_type=n["notification_type"],
            priority=n["priority"],
            trigger_reason=n["trigger_reason"],
            supporting_data=n["supporting_data"],
            ai_explanation=n["ai_explanation"],
            recommended_action=n["recommended_action"],
        )
        db.add(note)
        created += 1

    db.commit()
    return {"generated": created, "notifications": notes}


# ─────────────────────────────────────────────
# Goals
# ─────────────────────────────────────────────

@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new financial goal."""
    goal = Goal(
        user_id=current_user.id,
        title=payload.title,
        goal_type=payload.goal_type,
        target_amount=payload.target_amount,
        category=payload.category,
        deadline=payload.deadline,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/goals", response_model=List[GoalResponse])
def get_goals(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all goals for the authenticated user."""
    q = db.query(Goal).filter(Goal.user_id == current_user.id)
    if active_only:
        q = q.filter(Goal.is_active == True)
    return q.order_by(Goal.created_at.desc()).all()


@router.get("/goals/{goal_id}/evaluate", response_model=GoalResponse)
def evaluate_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluate goal progress using live transaction data."""
    from automation.goals.tracker import evaluate_goal as _eval

    goal = db.query(Goal).filter(
        Goal.id == goal_id, Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    stats = get_dashboard_summary(db, current_user.id)
    result = _eval(
        {
            "goal_type": goal.goal_type,
            "target_amount": goal.target_amount,
            "category": goal.category,
            "deadline": goal.deadline,
            "title": goal.title,
        },
        stats
    )

    goal.current_amount = result["current_amount"]
    goal.progress_percentage = result["progress_percentage"]
    goal.ai_prediction = result["ai_prediction"]
    goal.is_achieved = result["is_achieved"]
    from datetime import datetime
    goal.last_evaluated = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate a goal."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id, Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.is_active = False
    db.commit()
    return {"message": "Goal deactivated"}


# ─────────────────────────────────────────────
# Financial Health Score
# ─────────────────────────────────────────────

@router.get("/health-score")
def get_health_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate and return the current financial health score."""
    from datetime import datetime

    stats = get_dashboard_summary(db, current_user.id)

    # Inline score calculation — avoids import path issues on Railway deployment
    savings_rate = stats.get("savings_percentage", 0) / 100
    total_income = stats.get("total_income", 0)
    total_spending = stats.get("total_spending", 0)
    expense_ratio = total_spending / total_income if total_income > 0 else 1.0
    net_cash_flow = stats.get("net_cash_flow", 0)
    this_month = stats.get("this_month_spending", 0)
    avg_monthly = stats.get("average_monthly_spending", 0) or 1.0
    total_transactions = stats.get("total_transactions", 0)
    avg_daily = stats.get("average_daily_spending", 0) or 1.0
    today = stats.get("today_spending", 0)

    def score_savings(r): return 100 if r>=0.30 else 80 if r>=0.20 else 60 if r>=0.10 else 40 if r>=0.05 else 20 if r>=0 else 0
    def score_expense(r): return 100 if r<=0.50 else 80 if r<=0.70 else 60 if r<=0.85 else 40 if r<=1.0 else 0
    def score_cashflow(n, i): r=n/i if i>0 else 0; return 100 if r>=0.30 else 80 if r>=0.10 else 60 if r>=0 else 30 if r>=-0.10 else 0
    def score_trend(m, a): r=m/a if a>0 else 1; return 100 if r<=0.8 else 80 if r<=1.0 else 60 if r<=1.2 else 40 if r<=1.5 else 20
    def score_consistency(t): return 100 if t>=20 else 80 if t>=10 else 60 if t>=5 else 40
    def score_budget(a, t): r=t/a if a>0 else 1; return 100 if r<=1.0 else 70 if r<=1.5 else 40 if r<=2.0 else 10

    components = {
        "savings": score_savings(savings_rate),
        "expense": score_expense(expense_ratio),
        "cash_flow": score_cashflow(net_cash_flow, total_income),
        "trend": score_trend(this_month, avg_monthly),
        "consistency": score_consistency(total_transactions),
        "budget": score_budget(avg_daily, today),
    }
    weights = {"savings":0.25,"expense":0.20,"cash_flow":0.20,"trend":0.15,"consistency":0.10,"budget":0.10}
    score = round(sum(components[k]*weights[k] for k in weights), 1)
    grade = "A" if score>=80 else "B" if score>=65 else "C" if score>=50 else "D" if score>=35 else "F"

    messages = {"A":"Excellent financial health. You are saving consistently and managing expenses well.",
                "B":"Good financial health. Minor improvements could push you higher.",
                "C":"Average. Consider reviewing your largest expense categories.",
                "D":"Below average. Your expenses are too high relative to income.",
                "F":"Critical. Expenses exceed income. Urgent budget review required."}

    tips = []
    if components["savings"] < 60: tips.append("Increase your savings rate to at least 20% of income.")
    if components["expense"] < 60: tips.append("Reduce monthly expenses — identify and cut top 2 categories.")
    if components["cash_flow"] < 60: tips.append("Improve cash flow by reducing discretionary spending this month.")
    if components["trend"] < 60: tips.append("Your spending is rising. Set a weekly spending limit.")
    if not tips: tips.append("Keep up the good habits. Consider investing your savings.")

    return {
        "score": score,
        "grade": grade,
        "savings_component": components["savings"],
        "expense_component": components["expense"],
        "cash_flow_component": components["cash_flow"],
        "trend_component": components["trend"],
        "consistency_component": components["consistency"],
        "budget_component": components["budget"],
        "interpretation": messages[grade],
        "improvement_tips": tips,
        "calculated_at": datetime.utcnow().isoformat()
    }


# ─────────────────────────────────────────────
# AI Insights
# ─────────────────────────────────────────────

@router.get("/insights", response_model=List[InsightResponse])
def get_insights(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get stored AI insights for the authenticated user."""
    return db.query(AIInsight).filter(
        AIInsight.user_id == current_user.id
    ).order_by(AIInsight.generated_at.desc()).limit(limit).all()


@router.post("/insights/generate")
def generate_insights_now(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate fresh insights from current transaction data."""
    from automation.insights.generator import generate_insights

    stats = get_dashboard_summary(db, current_user.id)
    try:
        merchant_data = get_merchant_analytics(db, current_user.id)
        behaviour_data = get_spending_behaviour(db, current_user.id)
    except Exception:
        merchant_data = {}
        behaviour_data = {}

    insights = generate_insights(stats, merchant_data, behaviour_data)
    created = 0

    for insight in insights:
        rec = AIInsight(
            user_id=current_user.id,
            insight_type=insight["insight_type"],
            title=insight["title"],
            description=insight["description"],
            supporting_metric=insight["supporting_metric"],
            change_percentage=insight.get("change_percentage", 0),
            is_positive=insight.get("is_positive", True),
        )
        db.add(rec)
        created += 1

    db.commit()
    return {"generated": created, "insights": insights}


# ─────────────────────────────────────────────
# Admin / Monitoring
# ─────────────────────────────────────────────

@router.get("/admin/job-logs", response_model=List[JobLogResponse])
def get_job_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View background job execution history (admin)."""
    return db.query(JobLog).order_by(JobLog.started_at.desc()).limit(limit).all()


@router.post("/admin/run-daily-analysis")
def trigger_daily_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger the daily analysis job."""
    from automation.jobs.financial_jobs import run_daily_analysis
    background_tasks.add_task(run_daily_analysis)
    return {"message": "Daily analysis job triggered in background"}


@router.post("/admin/retrain-models")
def trigger_model_retraining(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger ML model retraining."""
    from automation.jobs.financial_jobs import run_model_retraining
    background_tasks.add_task(run_model_retraining)
    return {"message": "Model retraining triggered in background"}


@router.get("/admin/scheduler-status")
def get_scheduler_status(current_user: User = Depends(get_current_user)):
    """View current status of scheduled jobs."""
    from automation.scheduler.scheduler import get_scheduler_status
    return get_scheduler_status()

"""
Module 1 & 2 – Background Jobs
All scheduled and on-demand background tasks.
Jobs are pure functions — they open their own DB sessions and close them cleanly.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.transaction import Transaction as TxnModel  # avoids SQLAlchemy internal name clash
from app.models.automation import Notification, FinancialHealthScore, AIInsight, JobLog

from app.services.dashboard_service import get_dashboard_summary
from app.services.analytics_service import get_merchant_analytics, get_spending_behaviour

from automation.scoring.health_score import calculate_health_score
from automation.insights.generator import generate_insights
from automation.notifications.engine import generate_notifications


def _log_job(db, job_name: str, status: str, started_at: datetime,
             records: int = 0, error: str = None):
    """Write a job execution record."""
    log = JobLog(
        job_name=job_name,
        status=status,
        started_at=started_at,
        completed_at=datetime.utcnow(),
        duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        records_processed=records,
        error_message=error,
    )
    db.add(log)
    db.commit()


def run_daily_analysis():
    """
    Daily job — runs for every active user:
    1. Recalculate financial health score
    2. Generate AI insights
    3. Generate smart notifications
    Store results in DB.
    """
    # Ensure all tables exist (important when running outside FastAPI)
    Base.metadata.create_all(bind=engine)

    job_name = "daily_analysis"
    started_at = datetime.utcnow()
    print(f"[{started_at}] ▶ Running {job_name}...")

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        processed = 0

        for user in users:
            try:
                stats = get_dashboard_summary(db, user.id)

                # ── Health Score ──
                score_data = calculate_health_score(stats)
                health = FinancialHealthScore(
                    user_id=user.id,
                    score=score_data["score"],
                    grade=score_data["grade"],
                    savings_component=score_data["savings_component"],
                    expense_component=score_data["expense_component"],
                    consistency_component=score_data["consistency_component"],
                    cash_flow_component=score_data["cash_flow_component"],
                    trend_component=score_data["trend_component"],
                    interpretation=score_data["interpretation"],
                    improvement_tips=json.dumps(score_data["improvement_tips"]),
                )
                db.add(health)

                # ── Insights ──
                try:
                    merchant_data = get_merchant_analytics(db, user.id)
                    behaviour_data = get_spending_behaviour(db, user.id)
                except Exception:
                    merchant_data = {}
                    behaviour_data = {}

                insights = generate_insights(stats, merchant_data, behaviour_data)
                for insight in insights:
                    rec = AIInsight(
                        user_id=user.id,
                        insight_type=insight["insight_type"],
                        title=insight["title"],
                        description=insight["description"],
                        supporting_metric=insight["supporting_metric"],
                        change_percentage=insight.get("change_percentage", 0),
                        is_positive=insight.get("is_positive", True),
                    )
                    db.add(rec)

                # ── Notifications ──
                notifications = generate_notifications(user_stats=stats)
                for n in notifications:
                    note = Notification(
                        user_id=user.id,
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

                db.commit()
                processed += 1

            except Exception as e:
                print(f"  ⚠️  Error processing user {user.id}: {e}")
                db.rollback()

        _log_job(db, job_name, "success", started_at, records=processed)
        print(f"  ✅ {job_name} complete — {processed} users processed")

    except Exception as e:
        _log_job(db, job_name, "failed", started_at, error=str(e))
        print(f"  ❌ {job_name} failed: {e}")
    finally:
        db.close()


def run_model_retraining():
    """
    Scheduled retraining job.
    Rebuilds the ML dataset and retrains all models.
    Only runs if enough new transactions exist since last training.
    """
    job_name = "model_retraining"
    started_at = datetime.utcnow()
    print(f"[{started_at}] ▶ Running {job_name}...")

    db = SessionLocal()
    try:
        from ml.pipelines.train_all import train_all
        train_all()
        _log_job(db, job_name, "success", started_at)
        print(f"  ✅ {job_name} complete")
    except Exception as e:
        _log_job(db, job_name, "failed", started_at, error=str(e))
        print(f"  ❌ {job_name} failed: {e}")
    finally:
        db.close()

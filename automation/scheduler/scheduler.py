"""
Module 1 – Scheduler
APScheduler configuration. Runs inside the FastAPI process.
Started and stopped via FastAPI lifespan events.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from automation.jobs.financial_jobs import run_daily_analysis, run_model_retraining

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def setup_jobs():
    """Register all scheduled jobs."""

    # Daily analysis — runs at 8:00 AM every day
    scheduler.add_job(
        run_daily_analysis,
        trigger=CronTrigger(hour=8, minute=0),
        id="daily_analysis",
        name="Daily Financial Analysis",
        replace_existing=True,
        max_instances=1,          # never run twice simultaneously
        misfire_grace_time=3600,  # allow up to 1 hour late start
    )

    # Weekly model retraining — runs every Sunday at 2:00 AM
    scheduler.add_job(
        run_model_retraining,
        trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="model_retraining",
        name="Weekly Model Retraining",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=7200,
    )

    logger.info("Scheduler jobs registered")


def start_scheduler():
    setup_jobs()
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


def get_scheduler_status() -> dict:
    """Return current status of all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })
    return {
        "running": scheduler.running,
        "jobs": jobs,
    }

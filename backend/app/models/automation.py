"""
Automation Models
Tables for notifications, goals, financial health scores, job logs, insights.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)     # "alert" | "insight" | "goal" | "report"
    priority = Column(String, default="medium")  # "high" | "medium" | "low"
    trigger_reason = Column(Text)          # why was this triggered
    supporting_data = Column(Text)         # JSON string of relevant data
    ai_explanation = Column(Text)          # human-readable AI basis
    recommended_action = Column(Text)      # what the user should do
    is_read = Column(Boolean, default=False)
    delivered_via = Column(String, default="in_app")
    created_at = Column(DateTime, default=datetime.utcnow)


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    goal_type = Column(String)             # "save" | "limit_category" | "emergency_fund"
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    category = Column(String)              # relevant category if applicable
    deadline = Column(String)             # DD/MM/YY
    is_active = Column(Boolean, default=True)
    is_achieved = Column(Boolean, default=False)
    progress_percentage = Column(Float, default=0.0)
    ai_prediction = Column(String)         # "on_track" | "at_risk" | "achieved" | "failed"
    last_evaluated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class FinancialHealthScore(Base):
    __tablename__ = "financial_health_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)          # 0-100
    grade = Column(String)                         # A/B/C/D/F
    savings_component = Column(Float)
    expense_component = Column(Float)
    consistency_component = Column(Float)
    cash_flow_component = Column(Float)
    trend_component = Column(Float)
    interpretation = Column(Text)
    improvement_tips = Column(Text)               # JSON list
    calculated_at = Column(DateTime, default=datetime.utcnow)


class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, nullable=False)
    status = Column(String)                       # "running" | "success" | "failed"
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_type = Column(String)                 # "spending" | "saving" | "behaviour"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    supporting_metric = Column(String)
    change_percentage = Column(Float)
    is_positive = Column(Boolean, default=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

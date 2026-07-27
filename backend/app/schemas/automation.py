from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    priority: str
    trigger_reason: str
    ai_explanation: str
    recommended_action: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    goal_type: str          # "save" | "limit_category" | "limit_spending" | "emergency_fund"
    target_amount: float
    category: Optional[str] = None
    deadline: Optional[str] = None  # DD/MM/YY

    @field_validator("target_amount")
    @classmethod
    def validate_target(cls, v):
        if v <= 0:
            raise ValueError("target_amount must be greater than 0")
        return v

    @field_validator("goal_type")
    @classmethod
    def validate_goal_type(cls, v):
        valid = {"save", "limit_category", "limit_spending", "emergency_fund"}
        if v not in valid:
            raise ValueError(f"goal_type must be one of {valid}")
        return v


class GoalResponse(BaseModel):
    id: int
    title: str
    goal_type: str
    target_amount: float
    current_amount: float
    category: Optional[str]
    deadline: Optional[str]
    is_active: bool
    is_achieved: bool
    progress_percentage: float
    ai_prediction: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthScoreResponse(BaseModel):
    score: float
    grade: str
    savings_component: float
    expense_component: float
    consistency_component: float
    cash_flow_component: float
    trend_component: float
    interpretation: str
    improvement_tips: Any
    calculated_at: datetime

    class Config:
        from_attributes = True


class InsightResponse(BaseModel):
    id: int
    insight_type: str
    title: str
    description: str
    supporting_metric: Optional[str]
    change_percentage: Optional[float]
    is_positive: bool
    generated_at: datetime

    class Config:
        from_attributes = True


class JobLogResponse(BaseModel):
    id: int
    job_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    records_processed: int
    error_message: Optional[str]

    class Config:
        from_attributes = True

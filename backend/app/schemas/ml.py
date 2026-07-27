from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class UserFeaturesRequest(BaseModel):
    """
    Client sends key financial metrics.
    The prediction service maps these to model feature vectors.
    """
    balance: Optional[float] = None
    rolling_7d_avg: Optional[float] = None
    rolling_30d_avg: Optional[float] = None
    spending_velocity: Optional[float] = None
    savings_rate: Optional[float] = None
    expense_ratio: Optional[float] = None
    net_cash_flow: Optional[float] = None
    days_since_last_txn: Optional[float] = None
    merchant_diversity: Optional[float] = None
    category_concentration: Optional[float] = None
    total_user_expense: Optional[float] = None


class SpendingPredictionResponse(BaseModel):
    predicted_amount: float
    currency: str
    model_version: str
    algorithm: str
    explanation: Dict[str, Any]
    model_metrics: Dict[str, Any]


class CashExhaustionResponse(BaseModel):
    days_until_low_balance: Optional[float]
    threshold: Optional[float]
    low_balance_risk: Optional[int]
    risk_probability: Optional[float]


class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    interpretation: str
    model_version: str


class RecommendationItem(BaseModel):
    title: str
    message: str
    priority: str
    category: str
    basis: str


class RecommendationsResponse(BaseModel):
    total_recommendations: int
    recommendations: List[RecommendationItem]

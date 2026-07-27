"""
Module 9 – FastAPI ML Endpoints
All ML predictions exposed as authenticated REST APIs.
Routes call prediction_service only — no ML logic here.
"""
import sys
from pathlib import Path

# Allow importing from ml/ folder which is outside backend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.ml import (
    UserFeaturesRequest,
    SpendingPredictionResponse,
    CashExhaustionResponse,
    AnomalyDetectionResponse,
    RecommendationsResponse,
)
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/api/v1/ml", tags=["ML"])


def _get_prediction_service():
    """Lazy import to avoid loading ML models at server start if not needed."""
    from ml.services.prediction_service import prediction_service
    return prediction_service


@router.post("/predict-spending", response_model=SpendingPredictionResponse)
def predict_spending(
    features: UserFeaturesRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Predict the next transaction amount for the authenticated user.
    Provide recent financial metrics as features.
    """
    svc = _get_prediction_service()
    result = svc.predict_spending(features.model_dump())
    
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["error"])
    
    return result


@router.post("/predict-cash-exhaustion", response_model=CashExhaustionResponse)
def predict_cash_exhaustion(
    features: UserFeaturesRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Predict days until balance drops below threshold and 30-day risk score.
    """
    svc = _get_prediction_service()
    result = svc.predict_cash_exhaustion(features.model_dump())
    return result


@router.post("/detect-anomaly", response_model=AnomalyDetectionResponse)
def detect_anomaly(
    features: UserFeaturesRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Check if a transaction's features are anomalous compared to user history.
    """
    svc = _get_prediction_service()
    result = svc.detect_anomaly(features.model_dump())
    
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["error"])
    
    return result


@router.post("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    features: UserFeaturesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get personalised financial recommendations.
    Combines ML model signals with business rules.
    """
    # Pull live stats from dashboard service
    user_stats = get_dashboard_summary(db, current_user.id)
    
    svc = _get_prediction_service()
    result = svc.get_recommendations(
        user_stats=user_stats,
        user_features=features.model_dump(),
    )
    return result


@router.get("/model-info")
def get_model_info(current_user: User = Depends(get_current_user)):
    """
    Get status and version of all trained ML models.
    """
    svc = _get_prediction_service()
    return svc.get_all_model_info()

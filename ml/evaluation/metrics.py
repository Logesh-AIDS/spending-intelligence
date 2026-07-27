"""
Model Evaluation Metrics
Centralised metrics for all model types.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    silhouette_score, davies_bouldin_score,
    confusion_matrix
)
from typing import Dict, Any


def regression_metrics(y_true, y_pred) -> Dict[str, float]:
    """MAE, MSE, RMSE, R² for regression models."""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    return {
        "mae": round(mae, 4),
        "mse": round(mse, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
    }


def classification_metrics(y_true, y_pred, average="binary") -> Dict[str, float]:
    """Accuracy, precision, recall, F1 for classification models."""
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, average=average, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, average=average, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, average=average, zero_division=0), 4),
    }


def clustering_metrics(X, labels) -> Dict[str, float]:
    """Silhouette and Davies-Bouldin scores for clustering."""
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    if n_clusters < 2:
        return {"silhouette": -1.0, "davies_bouldin": -1.0}
    return {
        "silhouette": round(silhouette_score(X, labels), 4),
        "davies_bouldin": round(davies_bouldin_score(X, labels), 4),
    }


def compare_models(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compare multiple models side by side.
    Args:
        results: {"ModelName": {"mae": .., "rmse": .., "r2": ..}}
    Returns:
        DataFrame sorted by RMSE (lower = better)
    """
    df = pd.DataFrame(results).T
    if "rmse" in df.columns:
        df = df.sort_values("rmse")
    return df


def print_metrics(model_name: str, metrics: Dict[str, float]):
    print(f"\n  📊 {model_name}:")
    for k, v in metrics.items():
        print(f"     {k}: {v}")

"""
Module 1 – Spending Prediction (Regression)
Trains and compares 6 regression algorithms to predict transaction amounts.
Saves the best performing model based on RMSE.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from ml.evaluation.metrics import regression_metrics, compare_models, print_metrics
from ml.inference.persistence import save_model
from ml.config.config import FEATURES_DATASET_PATH, RANDOM_SEED


# Features used for spending prediction
# These are the features a model can know BEFORE the next transaction
SPENDING_FEATURES = [
    "day_of_week", "day", "month", "quarter", "week_of_year",
    "is_weekend", "days_until_month_end",
    "rolling_7d_avg", "rolling_30d_avg",
    "rolling_7d_sum", "rolling_30d_sum",
    "spending_velocity", "days_since_last_txn",
    "merchant_frequency", "merchant_diversity", "repeat_merchant",
    "category_frequency", "category_concentration",
    "log_amount", "amount_vs_avg_ratio",
    "savings_rate", "expense_ratio", "net_cash_flow",
    "transaction_type_encoded", "category_encoded",
]

TARGET = "amount"


def load_training_data():
    """Load feature dataset and filter to debit transactions only."""
    df = pd.read_csv(FEATURES_DATASET_PATH)
    
    # Predict spending — use debit transactions only
    df = df[df["transaction_type"] == "Debit"].copy()
    
    if len(df) < 5:
        raise ValueError(f"Not enough debit transactions to train. Found {len(df)}, need at least 5.")
    
    # Keep only columns that exist
    available = [c for c in SPENDING_FEATURES if c in df.columns]
    
    X = df[available].fillna(0)
    y = df[TARGET]
    
    return X, y, available


def train_all_models():
    """
    Train and compare all regression algorithms.
    Returns the best model based on lowest RMSE on test set.
    """
    print("\n" + "=" * 60)
    print("  MODULE 1 — SPENDING PREDICTION (REGRESSION)")
    print("=" * 60)
    
    X, y, feature_cols = load_training_data()
    print(f"\n  Training data: {len(X)} samples, {len(feature_cols)} features")
    
    # Split — use time ordering (not random) for financial data
    # Earlier transactions train the model, later ones test it
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Scale — fit only on training data to prevent data leakage
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # Define all candidate algorithms
    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Lasso": Lasso(alpha=0.1, max_iter=10000),
        "DecisionTree": DecisionTreeRegressor(max_depth=5, random_state=RANDOM_SEED),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=RANDOM_SEED),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=RANDOM_SEED),
    }
    
    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBRegressor(n_estimators=100, max_depth=4, random_state=RANDOM_SEED, verbosity=0)
    
    # Train and evaluate each model
    all_metrics = {}
    trained_models = {}
    
    for name, model in models.items():
        # Tree models don't need scaling, linear models do
        if name in ["LinearRegression", "Ridge", "Lasso"]:
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
        
        metrics = regression_metrics(y_test, preds)
        all_metrics[name] = metrics
        trained_models[name] = model
        print_metrics(name, metrics)
    
    # Compare all models
    comparison = compare_models(all_metrics)
    print("\n  📋 Model Comparison (sorted by RMSE):")
    print(comparison.to_string())
    
    # Select best model by lowest RMSE
    best_name = comparison.index[0]
    best_model = trained_models[best_name]
    best_metrics = all_metrics[best_name]
    
    print(f"\n  🏆 Best Model: {best_name} (RMSE: {best_metrics['rmse']})")
    
    # Save best model with all artefacts
    # Retrain best model on full dataset for maximum data use
    if best_name in ["LinearRegression", "Ridge", "Lasso"]:
        X_full_s = scaler.fit_transform(X)
        best_model.fit(X_full_s, y)
    else:
        best_model.fit(X, y)
    
    save_model(
        model_name="spending_predictor",
        model=best_model,
        feature_cols=feature_cols,
        scaler=scaler,
        metrics=best_metrics,
        extra_metadata={
            "algorithm": best_name,
            "target": TARGET,
            "training_samples": len(X),
            "all_model_metrics": all_metrics,
        }
    )
    
    return best_model, scaler, feature_cols, best_metrics


if __name__ == "__main__":
    train_all_models()

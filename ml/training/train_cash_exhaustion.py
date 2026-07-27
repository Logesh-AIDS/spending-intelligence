"""
Module 2 – Cash Exhaustion Prediction
Predicts how many days until the user's balance drops below a threshold.

Label engineering: days_until_low_balance
- For each transaction, look ahead to find when balance drops below threshold
- This is a regression problem (predict N days)
- Also produces a risk_flag (binary: will balance drop within 30 days?)
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from ml.evaluation.metrics import regression_metrics, classification_metrics, print_metrics
from ml.inference.persistence import save_model
from ml.config.config import FEATURES_DATASET_PATH, RANDOM_SEED

LOW_BALANCE_THRESHOLD = 1000.0  # ₹1000 — considered critically low

# Features for cash exhaustion — balance trend focused
CASH_FEATURES = [
    "balance", "rolling_7d_sum", "rolling_30d_sum", "rolling_7d_avg",
    "spending_velocity", "savings_rate", "expense_ratio",
    "net_cash_flow", "days_since_last_txn",
    "day_of_week", "days_until_month_end",
    "transaction_type_encoded", "category_encoded",
]


def engineer_exhaustion_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each transaction row, calculate:
    - days_until_low_balance: how many future days until balance < threshold
    - low_balance_risk: 1 if balance will drop below threshold within 30 days
    
    Why this matters: A user can see "you'll run low in 12 days" and act early.
    """
    df = df.copy()
    df = df[df["balance"].notna()].sort_values(["user_id", "parsed_date"])
    
    labels = []
    for user_id, group in df.groupby("user_id"):
        group = group.reset_index(drop=True)
        
        for i in range(len(group)):
            current_balance = group.loc[i, "balance"]
            
            # Look ahead: find when balance first drops below threshold
            days_until_low = 999  # default: no exhaustion in dataset
            
            future = group.iloc[i+1:]
            for _, row in future.iterrows():
                if row["balance"] < LOW_BALANCE_THRESHOLD:
                    # Approximate days using date difference
                    try:
                        d1 = pd.to_datetime(group.loc[i, "parsed_date"])
                        d2 = pd.to_datetime(row["parsed_date"])
                        days_until_low = max((d2 - d1).days, 0)
                    except Exception:
                        days_until_low = 30
                    break
            
            labels.append({
                "index": group.index[i] if hasattr(group.index, '__iter__') else i,
                "days_until_low_balance": days_until_low,
                "low_balance_risk": 1 if days_until_low <= 30 else 0,
            })
    
    label_df = pd.DataFrame(labels)
    df = df.reset_index(drop=True)
    df["days_until_low_balance"] = label_df["days_until_low_balance"].values
    df["low_balance_risk"] = label_df["low_balance_risk"].values
    
    return df


def train_cash_exhaustion():
    print("\n" + "=" * 60)
    print("  MODULE 2 — CASH EXHAUSTION PREDICTION")
    print("=" * 60)
    
    df = pd.read_csv(FEATURES_DATASET_PATH)
    
    # Only rows with balance data
    df = df[df["balance"].notna()].copy()
    
    if len(df) < 5:
        print("  ⚠️  Not enough data with balance field. Skipping.")
        return
    
    # Engineer labels
    df = engineer_exhaustion_labels(df)
    
    available = [c for c in CASH_FEATURES if c in df.columns]
    X = df[available].fillna(0)
    
    # ── Regression: predict days_until_low_balance ──
    y_reg = df["days_until_low_balance"]
    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y_reg.iloc[:split], y_reg.iloc[split:]
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    gbr = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=RANDOM_SEED)
    gbr.fit(X_train, y_train)
    preds_reg = gbr.predict(X_test)
    metrics_reg = regression_metrics(y_test, preds_reg)
    print("\n  Regression (days until low balance):")
    print_metrics("GradientBoosting", metrics_reg)
    
    # ── Classification: will balance drop below threshold in 30 days? ──
    y_clf = df["low_balance_risk"]
    y_train_c = y_clf.iloc[:split]
    y_test_c = y_clf.iloc[split:]
    
    if y_train_c.nunique() > 1:
        clf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED)
        clf.fit(X_train, y_train_c)
        preds_clf = clf.predict(X_test)
        metrics_clf = classification_metrics(y_test_c, preds_clf)
        print("\n  Classification (30-day low balance risk):")
        print_metrics("RandomForest", metrics_clf)
    else:
        clf = None
        metrics_clf = {}
        print("  ⚠️  Only one class in labels — classification skipped (need more data)")
    
    # Save regression model
    save_model(
        model_name="cash_exhaustion_regressor",
        model=gbr,
        feature_cols=available,
        scaler=scaler,
        metrics=metrics_reg,
        extra_metadata={
            "threshold": LOW_BALANCE_THRESHOLD,
            "target": "days_until_low_balance",
        }
    )
    
    # Save classifier if trained
    if clf:
        save_model(
            model_name="cash_exhaustion_classifier",
            model=clf,
            feature_cols=available,
            scaler=scaler,
            metrics=metrics_clf,
            extra_metadata={
                "threshold": LOW_BALANCE_THRESHOLD,
                "target": "low_balance_risk_30d",
            }
        )
    
    print("\n  ✅ Cash exhaustion models saved")


if __name__ == "__main__":
    train_cash_exhaustion()

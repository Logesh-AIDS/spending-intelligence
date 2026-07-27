"""
Module 3 – Overspending & Anomaly Detection

Why Isolation Forest?
- Works without labelled anomaly data (unsupervised)
- Handles high-dimensional tabular data well
- Fast and interpretable contamination parameter
- Better than Z-score for non-Gaussian distributions (spending data is right-skewed)
- Better than LOF for this dataset size — LOF needs dense neighbourhoods

We also include Z-score as a statistical baseline for comparison.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from ml.evaluation.metrics import print_metrics
from ml.inference.persistence import save_model
from ml.config.config import FEATURES_DATASET_PATH, RANDOM_SEED

ANOMALY_FEATURES = [
    "amount", "log_amount", "rolling_7d_avg", "rolling_30d_avg",
    "spending_velocity", "days_since_last_txn",
    "amount_vs_avg_ratio", "merchant_frequency",
    "category_frequency", "is_weekend",
]

# Contamination: expected % of outliers in dataset
# 5% is a reasonable starting assumption for financial data
CONTAMINATION = 0.05


def zscore_detection(df: pd.DataFrame) -> pd.Series:
    """
    Z-score baseline: flag transactions more than 3 std devs from user mean.
    Simple but assumes normal distribution — not ideal for skewed spending.
    """
    flags = []
    for user_id, group in df.groupby("user_id"):
        mean = group["amount"].mean()
        std = group["amount"].std() or 1.0
        z_scores = (group["amount"] - mean) / std
        flags.extend((z_scores.abs() > 3).tolist())
    return pd.Series(flags, index=df.index)


def train_anomaly_detector():
    print("\n" + "=" * 60)
    print("  MODULE 3 — ANOMALY DETECTION")
    print("=" * 60)
    
    df = pd.read_csv(FEATURES_DATASET_PATH)
    debits = df[df["transaction_type"] == "Debit"].copy()
    
    if len(debits) < 5:
        print("  ⚠️  Not enough debit transactions. Skipping.")
        return
    
    available = [c for c in ANOMALY_FEATURES if c in debits.columns]
    X = debits[available].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # ── Compare approaches ──
    
    # 1. Isolation Forest (selected approach)
    iso = IsolationForest(contamination=CONTAMINATION, random_state=RANDOM_SEED)
    iso_labels = iso.fit_predict(X_scaled)          # -1 = anomaly, 1 = normal
    iso_scores = iso.score_samples(X_scaled)         # lower = more anomalous
    n_anomalies_iso = (iso_labels == -1).sum()
    print(f"\n  Isolation Forest: {n_anomalies_iso} anomalies detected ({n_anomalies_iso/len(X)*100:.1f}%)")
    
    # 2. Z-score (baseline for comparison)
    zscore_flags = zscore_detection(debits)
    n_anomalies_z = zscore_flags.sum()
    print(f"  Z-Score (>3 std): {n_anomalies_z} anomalies detected ({n_anomalies_z/len(X)*100:.1f}%)")
    
    # 3. LOF (comparison only — not saved as primary)
    lof = LocalOutlierFactor(contamination=CONTAMINATION)
    lof_labels = lof.fit_predict(X_scaled)
    n_anomalies_lof = (lof_labels == -1).sum()
    print(f"  Local Outlier Factor: {n_anomalies_lof} anomalies detected ({n_anomalies_lof/len(X)*100:.1f}%)")
    
    # Why Isolation Forest wins for this use case:
    # - Scales better to unseen transactions at inference time (predict() works on new data)
    # - LOF cannot predict on new data without refitting — unsuitable for real-time API
    # - Z-score assumes normality — spending is log-normal, not normal
    print("\n  → Selected: Isolation Forest (supports real-time inference, handles non-normal data)")
    
    # Log anomalous transactions for interpretability
    debits_with_flags = debits.copy()
    debits_with_flags["anomaly_score"] = iso_scores
    debits_with_flags["is_anomaly"] = (iso_labels == -1).astype(int)
    
    anomalies = debits_with_flags[debits_with_flags["is_anomaly"] == 1]
    if len(anomalies) > 0:
        print(f"\n  Sample anomalies detected:")
        for _, row in anomalies.head(3).iterrows():
            print(f"    ₹{row['amount']:.0f} to {row.get('merchant', '?')} on {row.get('date', '?')} (score: {row['anomaly_score']:.3f})")
    
    # Save Isolation Forest as primary anomaly model
    save_model(
        model_name="anomaly_detector",
        model=iso,
        feature_cols=available,
        scaler=scaler,
        metrics={"contamination": CONTAMINATION, "anomalies_found": int(n_anomalies_iso)},
        extra_metadata={
            "algorithm": "IsolationForest",
            "contamination": CONTAMINATION,
            "comparison": {
                "IsolationForest": int(n_anomalies_iso),
                "ZScore_3std": int(n_anomalies_z),
                "LocalOutlierFactor": int(n_anomalies_lof),
            }
        }
    )
    
    print("\n  ✅ Anomaly detector saved")


if __name__ == "__main__":
    train_anomaly_detector()

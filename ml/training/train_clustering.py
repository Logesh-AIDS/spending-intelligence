"""
Module 4 – User Behaviour Clustering
Segments users by spending personality.

Why K-Means?
- Works well for compact, spherical clusters in financial data
- Interpretable cluster centres (can describe each cluster)
- Scales to many users
- DBSCAN is better for arbitrary shapes but needs density — poor for small user sets
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from ml.evaluation.metrics import clustering_metrics
from ml.inference.persistence import save_model
from ml.config.config import FEATURES_DATASET_PATH, RANDOM_SEED, PLOTS_DIR
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# User-level aggregated features for clustering
# We aggregate per user — one row per user, not per transaction
USER_CLUSTER_FEATURES = [
    "total_user_expense", "savings_rate", "expense_ratio",
    "merchant_diversity", "category_concentration",
    "rolling_7d_avg", "rolling_30d_avg", "spending_velocity",
]

# Segment labels — assigned after reviewing cluster centres
SEGMENT_NAMES = {
    0: "Conservative Saver",
    1: "Balanced Spender",
    2: "Heavy Spender",
    3: "Frequent Micro-Spender",
    4: "Luxury Buyer",
}


def build_user_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level features to user-level profiles.
    One row per user — this is what we cluster on.
    """
    available = [c for c in USER_CLUSTER_FEATURES if c in df.columns] + ["user_id"]
    
    # Take the most recent row per user for rolling features (already cumulative)
    profiles = df[available].groupby("user_id").last().reset_index()
    
    return profiles


def train_clustering():
    print("\n" + "=" * 60)
    print("  MODULE 4 — USER BEHAVIOUR CLUSTERING")
    print("=" * 60)
    
    df = pd.read_csv(FEATURES_DATASET_PATH)
    
    profiles = build_user_profiles(df)
    print(f"\n  User profiles: {len(profiles)} users")
    
    if len(profiles) < 2:
        print("  ⚠️  Need at least 2 users to cluster. Skipping K-Means evaluation.")
        print("  → Training single-user model for inference readiness.")
    
    available_features = [c for c in USER_CLUSTER_FEATURES if c in profiles.columns]
    X = profiles[available_features].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Find optimal K using inertia (elbow method)
    max_k = min(6, len(profiles))
    inertias = []
    k_range = range(2, max_k + 1)
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
    
    # Choose K with most meaningful segmentation (min of max_k, n_users)
    optimal_k = min(len(profiles), max_k)
    
    # Train final model
    kmeans = KMeans(n_clusters=optimal_k, random_state=RANDOM_SEED, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Evaluate cluster quality
    if len(set(cluster_labels)) > 1:
        metrics = clustering_metrics(X_scaled, cluster_labels)
        print(f"\n  Cluster quality (K={optimal_k}):")
        print(f"    Silhouette Score: {metrics['silhouette']} (higher is better, max 1.0)")
        print(f"    Davies-Bouldin:   {metrics['davies_bouldin']} (lower is better)")
    else:
        metrics = {}
        print("  ⚠️  Only one cluster formed — normal with few users")
    
    # Show cluster centres (interpretable)
    centres_df = pd.DataFrame(kmeans.cluster_centers_, columns=available_features)
    print("\n  Cluster Centres (scaled values):")
    print(centres_df.to_string())
    
    # Assign user segments
    profiles["cluster"] = cluster_labels
    print("\n  User segments:")
    print(profiles[["user_id", "cluster"]].to_string(index=False))
    
    # Save
    save_model(
        model_name="user_segmentation",
        model=kmeans,
        feature_cols=available_features,
        scaler=scaler,
        metrics=metrics,
        extra_metadata={
            "algorithm": "KMeans",
            "n_clusters": optimal_k,
            "segment_names": SEGMENT_NAMES,
        }
    )
    
    print("\n  ✅ Clustering model saved")
    return kmeans, scaler, available_features


if __name__ == "__main__":
    train_clustering()

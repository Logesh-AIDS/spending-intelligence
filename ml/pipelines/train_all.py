"""
Master Training Pipeline
Runs the full data pipeline then trains all ML models.

Usage (from project root):
    python -m ml.pipelines.train_all
"""
from ml.pipelines.run_pipeline import run as run_data_pipeline
from ml.training.train_spending import train_all_models
from ml.training.train_cash_exhaustion import train_cash_exhaustion
from ml.training.train_anomaly import train_anomaly_detector
from ml.training.train_clustering import train_clustering


def train_all():
    print("\n🚀 MASTER TRAINING PIPELINE\n")

    # Step 1: Build ML dataset
    run_data_pipeline(skip_eda=True)

    # Step 2: Train all models
    print("\n" + "=" * 60)
    print("  TRAINING ALL ML MODELS")
    print("=" * 60)

    train_all_models()
    train_cash_exhaustion()
    train_anomaly_detector()
    train_clustering()

    print("\n✅ ALL MODELS TRAINED AND SAVED\n")


if __name__ == "__main__":
    train_all()

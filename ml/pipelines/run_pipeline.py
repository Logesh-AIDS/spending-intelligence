"""
ML Data Pipeline — Master Orchestrator
Runs the complete data engineering pipeline from database to ML-ready dataset.

Usage (from project root):
    python -m ml.pipelines.run_pipeline
    python -m ml.pipelines.run_pipeline --user_id 1
    python -m ml.pipelines.run_pipeline --skip_eda
"""
import argparse
from datetime import datetime

from ml.dataset.builder import build_raw_dataset, get_dataset_summary
from ml.validation.validator import validate_dataset
from ml.feature_engineering.features import engineer_features
from ml.preprocessing.preprocessor import clean_dataset, encode_categoricals, preprocess
from ml.eda.analysis import run_eda
from ml.config.config import (
    RAW_DATASET_PATH, VALIDATED_DATASET_PATH, FEATURES_DATASET_PATH
)


def run(user_id: int = None, skip_eda: bool = False, incremental_from: str = None):
    """
    Execute the complete ML data pipeline.
    
    Database → Extract → Validate → Clean → Feature Engineering
             → Preprocessing → EDA → ML-Ready Dataset
    """
    start = datetime.now()
    print("\n" + "=" * 60)
    print("  AI SPENDING INTELLIGENCE — ML DATA PIPELINE")
    print("=" * 60)

    # ─────────────────────────────────────────
    # Step 1 — Extract
    # ─────────────────────────────────────────
    print("\n📌 Step 1 — Dataset Extraction")
    df = build_raw_dataset(user_id=user_id, save=True)

    if len(df) == 0:
        print("❌ No transactions found in database. Seed some data first.")
        return

    summary = get_dataset_summary(df)
    print(f"   Total records: {summary['total_transactions']}")

    # ─────────────────────────────────────────
    # Step 2 — Validate
    # ─────────────────────────────────────────
    print("\n📌 Step 2 — Data Validation")
    validation_summary = validate_dataset(df)
    
    if not validation_summary["validation_passed"]:
        print(f"   ⚠️  {validation_summary['total_issues']} issues found — continuing with cleaning")

    # ─────────────────────────────────────────
    # Step 3 — Clean
    # ─────────────────────────────────────────
    print("\n📌 Step 3 — Data Cleaning")
    df = clean_dataset(df)

    # ─────────────────────────────────────────
    # Step 4 — Feature Engineering
    # ─────────────────────────────────────────
    print("\n📌 Step 4 — Feature Engineering")
    df = engineer_features(df, save=True)

    # ─────────────────────────────────────────
    # Step 5 — Preprocessing
    # ─────────────────────────────────────────
    print("\n📌 Step 5 — Preprocessing (Encoding)")
    df, encoders = encode_categoricals(df)
    df.to_csv(VALIDATED_DATASET_PATH, index=False)
    print(f"   💾 Preprocessed dataset saved to {VALIDATED_DATASET_PATH}")
    print(f"   Final shape: {df.shape[0]} rows × {df.shape[1]} columns")

    # ─────────────────────────────────────────
    # Step 6 — EDA (optional)
    # ─────────────────────────────────────────
    if not skip_eda:
        print("\n📌 Step 6 — Exploratory Data Analysis")
        run_eda(df)
    else:
        print("\n📌 Step 6 — EDA skipped (--skip_eda)")

    # ─────────────────────────────────────────
    # Done
    # ─────────────────────────────────────────
    elapsed = (datetime.now() - start).seconds
    print("\n" + "=" * 60)
    print(f"  ✅ PIPELINE COMPLETE in {elapsed}s")
    print(f"  Dataset: {VALIDATED_DATASET_PATH}")
    print(f"  Features: {FEATURES_DATASET_PATH}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ML data pipeline")
    parser.add_argument("--user_id", type=int, default=None, help="Filter by user ID")
    parser.add_argument("--skip_eda", action="store_true", help="Skip EDA plots")
    args = parser.parse_args()
    
    run(user_id=args.user_id, skip_eda=args.skip_eda)

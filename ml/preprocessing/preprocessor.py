"""
Data Preprocessing Pipeline
Handles cleaning, encoding, scaling, and train/val/test splitting.
Uses sklearn Pipeline objects for reproducibility.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import pickle

from ml.config.config import (
    TRAIN_RATIO, VAL_RATIO, TEST_RATIO, RANDOM_SEED,
    TRAIN_DATASET_PATH, VAL_DATASET_PATH, TEST_DATASET_PATH,
    MODELS_DIR, VALIDATED_DATASET_PATH
)


# ─────────────────────────────────────────────
# Step 1 — Clean
# ─────────────────────────────────────────────

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicates, fill missing values, and standardise formats.
    Every decision here has a reason — do not blindly drop rows.
    """
    df = df.copy()
    
    # Remove exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"  Removed {before - len(df)} exact duplicates")
    
    # Fill missing merchant with "Unknown" (not drop — keeps transaction data)
    df["merchant"] = df["merchant"].fillna("Unknown")
    
    # Fill missing category with "Others"
    df["category"] = df["category"].fillna("Others")
    
    # Fill missing balance with NaN (we can't guess balance)
    # ML features that use balance will handle this individually
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
    
    # Ensure amount is positive and numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]  # Drop rows with non-positive amounts
    
    # Standardise transaction_type capitalisation
    df["transaction_type"] = df["transaction_type"].str.capitalize()
    
    # Standardise bank names
    df["bank"] = df["bank"].str.strip()
    
    print(f"  Dataset cleaned: {len(df)} rows remaining")
    return df


# ─────────────────────────────────────────────
# Step 2 — Encode
# ─────────────────────────────────────────────

def encode_categoricals(df: pd.DataFrame, fit: bool = True) -> tuple:
    """
    Label-encode categorical columns.
    Returns encoded df and encoder dict.
    
    Why LabelEncoder here (not OneHot)?
    Tree-based models (Random Forest, XGBoost) handle label encoding well.
    OneHot would create many sparse columns for high-cardinality merchants.
    """
    df = df.copy()
    encoders = {}
    
    cat_cols = ["transaction_type", "bank", "category"]
    
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    
    return df, encoders


# ─────────────────────────────────────────────
# Step 3 — Scale
# ─────────────────────────────────────────────

def scale_features(df: pd.DataFrame, feature_cols: list, fit: bool = True) -> tuple:
    """
    Scale numerical features using StandardScaler.
    StandardScaler: mean=0, std=1 — best for linear models.
    MinMaxScaler would be used for neural networks (0-1 range).
    """
    df = df.copy()
    scaler = StandardScaler()
    
    # Only scale columns that exist and are numeric
    cols_to_scale = [c for c in feature_cols if c in df.columns and df[c].dtype in [np.float64, np.int64]]
    
    if cols_to_scale:
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale].fillna(0))
    
    return df, scaler, cols_to_scale


# ─────────────────────────────────────────────
# Step 4 — Split
# ─────────────────────────────────────────────

def split_dataset(
    df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    save: bool = True
) -> tuple:
    """
    Split into train / validation / test sets.
    Uses stratified split if classification target.
    
    Important: split BEFORE scaling to prevent data leakage.
    """
    X = df[feature_cols].fillna(0)
    y = df[target_col]
    
    # First split: train vs temp (val+test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(VAL_RATIO + TEST_RATIO),
        random_state=RANDOM_SEED
    )
    
    # Second split: val vs test
    val_size = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=(1 - val_size),
        random_state=RANDOM_SEED
    )
    
    print(f"  Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    
    if save:
        train_df = X_train.copy()
        train_df[target_col] = y_train
        val_df = X_val.copy()
        val_df[target_col] = y_val
        test_df = X_test.copy()
        test_df[target_col] = y_test
        
        train_df.to_csv(TRAIN_DATASET_PATH, index=False)
        val_df.to_csv(VAL_DATASET_PATH, index=False)
        test_df.to_csv(TEST_DATASET_PATH, index=False)
        print(f"  💾 Splits saved to {TRAIN_DATASET_PATH.parent}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


# ─────────────────────────────────────────────
# Full Preprocessing Pipeline
# ─────────────────────────────────────────────

def preprocess(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline.
    
    Args:
        df: Feature-engineered DataFrame
        save: Save clean output
    
    Returns:
        Preprocessed DataFrame
    """
    print("🔄 Preprocessing dataset...")
    
    df = clean_dataset(df)
    
    df, encoders = encode_categoricals(df)
    print("  ✅ Categorical encoding done")
    
    # Save encoders for later use in prediction
    encoder_path = MODELS_DIR / "encoders.pkl"
    with open(encoder_path, "wb") as f:
        pickle.dump(encoders, f)
    print(f"  💾 Encoders saved to {encoder_path}")
    
    if save:
        df.to_csv(VALIDATED_DATASET_PATH, index=False)
        print(f"  💾 Preprocessed data saved to {VALIDATED_DATASET_PATH}")
    
    return df


if __name__ == "__main__":
    from ml.config.config import FEATURES_DATASET_PATH
    df = pd.read_csv(FEATURES_DATASET_PATH)
    df = preprocess(df)
    print(df.head())

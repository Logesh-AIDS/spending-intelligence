"""
Dataset Builder
Extracts transaction data from SQLite into pandas DataFrames.
Supports full export and incremental updates.
"""
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

from ml.config.config import DATABASE_URL, RAW_DATASET_PATH, RAW_COLUMNS


def extract_transactions(user_id: int = None, date_from: str = None) -> pd.DataFrame:
    """
    Extract transactions from the database.
    
    Args:
        user_id: Filter by specific user (None = all users)
        date_from: Extract only transactions from this date forward (DD/MM/YY format)
    
    Returns:
        DataFrame with all transaction data
    """
    engine = create_engine(DATABASE_URL)
    
    query = "SELECT * FROM transactions"
    filters = []
    
    if user_id is not None:
        filters.append(f"user_id = {user_id}")
    
    if date_from:
        filters.append(f"date >= '{date_from}'")
    
    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    query += " ORDER BY created_at ASC"
    
    df = pd.read_sql(query, engine)
    engine.dispose()
    
    return df


def extract_users() -> pd.DataFrame:
    """
    Extract user data from the database.
    Useful for joining user metadata into features.
    """
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT id, email, full_name, is_active, created_at FROM users", engine)
    engine.dispose()
    return df


def build_raw_dataset(user_id: int = None, save: bool = True) -> pd.DataFrame:
    """
    Build the raw dataset by extracting all transactions.
    Optionally joins user info.
    
    Args:
        user_id: Filter by user (None = all)
        save: Save to CSV
    
    Returns:
        Raw transaction DataFrame
    """
    print("📊 Extracting transactions from database...")
    df = extract_transactions(user_id=user_id)
    
    print(f"✅ Extracted {len(df)} transactions")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Users: {df['user_id'].nunique()}")
    print(f"   Total amount: ${df['amount'].sum():,.2f}")
    
    if save:
        df.to_csv(RAW_DATASET_PATH, index=False)
        print(f"💾 Saved to {RAW_DATASET_PATH}")
    
    return df


def build_incremental_dataset(date_from: str, user_id: int = None) -> pd.DataFrame:
    """
    Build an incremental dataset from a specific date forward.
    Useful for adding new transactions to an existing dataset.
    
    Args:
        date_from: DD/MM/YY format
        user_id: Filter by user
    
    Returns:
        New transactions DataFrame
    """
    print(f"📊 Extracting incremental transactions from {date_from}...")
    df = extract_transactions(user_id=user_id, date_from=date_from)
    print(f"✅ Extracted {len(df)} new transactions")
    return df


def get_dataset_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of the dataset.
    
    Returns:
        Dictionary with dataset statistics
    """
    return {
        "total_transactions": len(df),
        "unique_users": df["user_id"].nunique(),
        "date_range": f"{df['date'].min()} to {df['date'].max()}",
        "total_amount": df["amount"].sum(),
        "debit_count": (df["transaction_type"] == "Debit").sum(),
        "credit_count": (df["transaction_type"] == "Credit").sum(),
        "unique_merchants": df["merchant"].nunique(),
        "unique_categories": df["category"].nunique(),
        "missing_values": df.isnull().sum().to_dict(),
    }


if __name__ == "__main__":
    # Example usage — run from project root: python -m ml.dataset.builder
    df = build_raw_dataset()
    summary = get_dataset_summary(df)
    print("\n📈 Dataset Summary:")
    for k, v in summary.items():
        print(f"   {k}: {v}")

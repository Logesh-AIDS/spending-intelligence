"""
Feature Engineering
Transforms raw transactions into ML-ready features.
One row per transaction, with historical context features added.
"""
import pandas as pd
import numpy as np
from datetime import datetime

from ml.config.config import DATE_FORMAT, FEATURES_DATASET_PATH


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DD/MM/YY string dates to datetime objects and extract components."""
    df = df.copy()
    df["parsed_date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
    df["day_of_week"] = df["parsed_date"].dt.dayofweek       # 0=Monday, 6=Sunday
    df["day_name"] = df["parsed_date"].dt.day_name()
    df["day"] = df["parsed_date"].dt.day
    df["month"] = df["parsed_date"].dt.month
    df["year"] = df["parsed_date"].dt.year
    df["quarter"] = df["parsed_date"].dt.quarter
    df["week_of_year"] = df["parsed_date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)  # 1=weekend
    
    # Days until month end
    df["days_in_month"] = df["parsed_date"].dt.days_in_month
    df["days_until_month_end"] = df["days_in_month"] - df["day"]
    
    return df


def add_amount_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add amount-related features per user."""
    df = df.copy()
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        debits = group[group["transaction_type"] == "Debit"]["amount"]
        
        # Log transform — reduces impact of outliers (₹10 vs ₹10,000)
        df.loc[idx, "log_amount"] = np.log1p(group["amount"])
        
        # Relative to user's own average (how unusual is this transaction)
        user_avg = debits.mean() if len(debits) > 0 else 1.0
        df.loc[idx, "amount_vs_avg_ratio"] = group["amount"] / user_avg
    
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rolling window features — capture spending momentum.
    Rolling 7-day and 30-day averages show recent trends.
    """
    df = df.copy()
    df = df.sort_values(["user_id", "parsed_date"])
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        debits_mask = group["transaction_type"] == "Debit"
        
        # Use amount as 0 for credit rows in spending calculations
        spend_series = group["amount"].where(debits_mask, 0)
        
        # Rolling sum and average (7-day and 30-day)
        rolling_7 = spend_series.rolling(window=7, min_periods=1)
        rolling_30 = spend_series.rolling(window=30, min_periods=1)
        
        df.loc[idx, "rolling_7d_avg"] = rolling_7.mean().round(2)
        df.loc[idx, "rolling_7d_sum"] = rolling_7.sum().round(2)
        df.loc[idx, "rolling_30d_avg"] = rolling_30.mean().round(2)
        df.loc[idx, "rolling_30d_sum"] = rolling_30.sum().round(2)
        
        # Spending velocity: how fast spending is changing
        # (7-day avg - 30-day avg) / 30-day avg — positive means accelerating spend
        rolling_7_vals = df.loc[idx, "rolling_7d_avg"]
        rolling_30_vals = df.loc[idx, "rolling_30d_avg"]
        velocity = (rolling_7_vals - rolling_30_vals) / rolling_30_vals.replace(0, np.nan)
        df.loc[idx, "spending_velocity"] = velocity.round(4)
    
    return df


def add_time_since_last_transaction(df: pd.DataFrame) -> pd.DataFrame:
    """Days since last transaction — measures transaction frequency."""
    df = df.copy()
    df = df.sort_values(["user_id", "parsed_date"])
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        time_diff = group["parsed_date"].diff().dt.days.fillna(0)
        df.loc[idx, "days_since_last_txn"] = time_diff
    
    return df


def add_merchant_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merchant-level features — capture merchant behaviour patterns.
    Repeat merchant rate shows loyalty/habit patterns.
    """
    df = df.copy()
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        
        merchant_counts = group["merchant"].value_counts()
        merchant_total = group.groupby("merchant")["amount"].sum()
        
        total_merchants = group["merchant"].nunique()
        
        # Merchant frequency — how often does this merchant appear (0-1)
        df.loc[idx, "merchant_frequency"] = group["merchant"].map(
            merchant_counts / len(group)
        )
        
        # Merchant diversity — number of unique merchants (same for all rows of user)
        df.loc[idx, "merchant_diversity"] = total_merchants
        
        # Repeat merchant ratio — % of transactions to already-seen merchants
        # Cumulative: has this merchant been seen before this row?
        seen_merchants = set()
        repeat_flags = []
        for merchant in group["merchant"]:
            if merchant in seen_merchants:
                repeat_flags.append(1)
            else:
                repeat_flags.append(0)
                seen_merchants.add(merchant)
        df.loc[idx, "repeat_merchant"] = repeat_flags
    
    return df


def add_category_features(df: pd.DataFrame) -> pd.DataFrame:
    """Category frequency and concentration per user."""
    df = df.copy()
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        
        cat_counts = group["category"].value_counts()
        total = len(group)
        
        # Category frequency (0-1)
        df.loc[idx, "category_frequency"] = group["category"].map(
            cat_counts / total
        )
        
        # Category concentration (HHI — higher means spending concentrated in fewer categories)
        cat_shares = cat_counts / total
        hhi = (cat_shares ** 2).sum()
        df.loc[idx, "category_concentration"] = hhi
    
    return df


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Financial health features — running balance, net cash flow, savings rate.
    These are critical for the spending forecast and cash exhaustion models.
    """
    df = df.copy()
    df = df.sort_values(["user_id", "parsed_date"])
    
    for user_id, group in df.groupby("user_id"):
        idx = group.index
        
        # Signed amount: positive for credits, negative for debits
        signed = group["amount"].where(
            group["transaction_type"] == "Credit",
            -group["amount"]
        )
        
        df.loc[idx, "signed_amount"] = signed
        
        # Running cumulative cash flow
        df.loc[idx, "cumulative_cash_flow"] = signed.cumsum()
        
        # Per-user totals for context
        total_income = group[group["transaction_type"] == "Credit"]["amount"].sum()
        total_expense = group[group["transaction_type"] == "Debit"]["amount"].sum()
        net = total_income - total_expense
        
        df.loc[idx, "total_user_income"] = total_income
        df.loc[idx, "total_user_expense"] = total_expense
        df.loc[idx, "net_cash_flow"] = net
        df.loc[idx, "savings_rate"] = round(net / total_income, 4) if total_income > 0 else 0.0
        df.loc[idx, "expense_ratio"] = round(total_expense / total_income, 4) if total_income > 0 else 1.0
    
    return df


def engineer_features(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """
    Run the full feature engineering pipeline.
    
    Args:
        df: Cleaned transaction DataFrame
        save: Save output to CSV
    
    Returns:
        Feature-rich DataFrame
    """
    print("⚙️  Engineering features...")
    
    df = parse_dates(df)
    print("  ✅ Date features")
    
    df = add_amount_features(df)
    print("  ✅ Amount features")
    
    df = add_rolling_features(df)
    print("  ✅ Rolling window features")
    
    df = add_time_since_last_transaction(df)
    print("  ✅ Time-since-last-transaction")
    
    df = add_merchant_features(df)
    print("  ✅ Merchant features")
    
    df = add_category_features(df)
    print("  ✅ Category features")
    
    df = add_financial_features(df)
    print("  ✅ Financial features")
    
    print(f"\n📐 Feature set: {len(df.columns)} columns, {len(df)} rows")
    
    if save:
        # Drop non-numeric columns not needed for ML before saving
        df.to_csv(FEATURES_DATASET_PATH, index=False)
        print(f"💾 Saved to {FEATURES_DATASET_PATH}")
    
    return df


if __name__ == "__main__":
    from ml.config.config import VALIDATED_DATASET_PATH
    df = pd.read_csv(VALIDATED_DATASET_PATH)
    df = engineer_features(df)
    print(df[["amount", "log_amount", "rolling_7d_avg", "spending_velocity", "savings_rate"]].head(10))

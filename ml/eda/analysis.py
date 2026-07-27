"""
Exploratory Data Analysis (EDA)
Generates visualisations and statistical summaries.
Saves all plots to ml/plots/.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — works without display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime

from ml.config.config import PLOTS_DIR, DATE_FORMAT

sns.set_theme(style="whitegrid", palette="muted")


def _save(name: str):
    path = PLOTS_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {path.name}")


# ─────────────────────────────────────────────
# 1. Spending Distribution
# ─────────────────────────────────────────────

def plot_spending_distribution(df: pd.DataFrame):
    """
    Shows how transaction amounts are distributed.
    Right-skewed is typical — few large transactions, many small ones.
    """
    debits = df[df["transaction_type"] == "Debit"]["amount"]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(debits, bins=30, edgecolor="black", color="steelblue")
    axes[0].set_title("Spending Distribution")
    axes[0].set_xlabel("Amount (₹)")
    
    axes[1].hist(np.log1p(debits), bins=30, edgecolor="black", color="seagreen")
    axes[1].set_title("Log-Spending Distribution")
    axes[1].set_xlabel("log(Amount + 1)")
    
    _save("spending_distribution")


# ─────────────────────────────────────────────
# 2. Category Distribution
# ─────────────────────────────────────────────

def plot_category_distribution(df: pd.DataFrame):
    """
    Which categories consume the most money.
    Helps validate if category auto-assignment is working.
    """
    debits = df[df["transaction_type"] == "Debit"]
    cat_totals = debits.groupby("category")["amount"].sum().sort_values(ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    cat_totals.plot(kind="barh", ax=ax, color="coral")
    ax.set_title("Spending by Category")
    ax.set_xlabel("Total Amount (₹)")
    _save("category_distribution")


# ─────────────────────────────────────────────
# 3. Merchant Distribution
# ─────────────────────────────────────────────

def plot_merchant_distribution(df: pd.DataFrame, top_n: int = 10):
    """Top merchants by total spending — shows who you pay most."""
    debits = df[(df["transaction_type"] == "Debit") & (df["merchant"] != "Unknown")]
    top = debits.groupby("merchant")["amount"].sum().nlargest(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top.sort_values().plot(kind="barh", ax=ax, color="mediumpurple")
    ax.set_title(f"Top {top_n} Merchants by Spending")
    ax.set_xlabel("Total Amount (₹)")
    _save("merchant_distribution")


# ─────────────────────────────────────────────
# 4. Daily Spending Trend
# ─────────────────────────────────────────────

def plot_daily_trend(df: pd.DataFrame):
    """Daily spending over time — shows spending momentum."""
    debits = df[df["transaction_type"] == "Debit"].copy()
    debits["parsed_date"] = pd.to_datetime(debits["date"], format=DATE_FORMAT, errors="coerce")
    daily = debits.groupby("parsed_date")["amount"].sum()
    
    fig, ax = plt.subplots(figsize=(14, 4))
    daily.plot(ax=ax, color="steelblue", linewidth=1.5)
    ax.set_title("Daily Spending Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    _save("daily_spending_trend")


# ─────────────────────────────────────────────
# 5. Monthly Spending Trend
# ─────────────────────────────────────────────

def plot_monthly_trend(df: pd.DataFrame):
    """Month-over-month spending — seasonal patterns visible here."""
    debits = df[df["transaction_type"] == "Debit"].copy()
    debits["parsed_date"] = pd.to_datetime(debits["date"], format=DATE_FORMAT, errors="coerce")
    debits["month"] = debits["parsed_date"].dt.to_period("M")
    monthly = debits.groupby("month")["amount"].sum()
    
    fig, ax = plt.subplots(figsize=(12, 4))
    monthly.plot(kind="bar", ax=ax, color="teal", edgecolor="black")
    ax.set_title("Monthly Spending Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    _save("monthly_spending_trend")


# ─────────────────────────────────────────────
# 6. Income vs Expense
# ─────────────────────────────────────────────

def plot_income_vs_expense(df: pd.DataFrame):
    """Visual comparison of income and spending by month."""
    df2 = df.copy()
    df2["parsed_date"] = pd.to_datetime(df2["date"], format=DATE_FORMAT, errors="coerce")
    df2["month"] = df2["parsed_date"].dt.to_period("M")
    
    income = df2[df2["transaction_type"] == "Credit"].groupby("month")["amount"].sum()
    expense = df2[df2["transaction_type"] == "Debit"].groupby("month")["amount"].sum()
    
    summary = pd.DataFrame({"Income": income, "Expense": expense}).fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    summary.plot(kind="bar", ax=ax, edgecolor="black")
    ax.set_title("Income vs Expense by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    _save("income_vs_expense")


# ─────────────────────────────────────────────
# 7. Balance History
# ─────────────────────────────────────────────

def plot_balance_history(df: pd.DataFrame):
    """Balance over time — declining trend signals cash risk."""
    has_balance = df[df["balance"].notna()].copy()
    has_balance["parsed_date"] = pd.to_datetime(has_balance["date"], format=DATE_FORMAT, errors="coerce")
    has_balance = has_balance.sort_values("parsed_date")
    
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(has_balance["parsed_date"], has_balance["balance"], color="darkorange", linewidth=1.5)
    ax.set_title("Account Balance Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance (₹)")
    _save("balance_history")


# ─────────────────────────────────────────────
# 8. Correlation Matrix
# ─────────────────────────────────────────────

def plot_correlation_matrix(df: pd.DataFrame):
    """Correlations between numerical features — guides feature selection."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Limit to meaningful columns to keep chart readable
    keep = [c for c in num_cols if c not in ["id", "user_id"]][:15]
    
    if len(keep) < 2:
        print("  ⚠️  Not enough numerical columns for correlation matrix")
        return
    
    corr = df[keep].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, linewidths=0.5)
    ax.set_title("Feature Correlation Matrix")
    _save("correlation_matrix")


# ─────────────────────────────────────────────
# 9. Spending by Day of Week
# ─────────────────────────────────────────────

def plot_day_of_week(df: pd.DataFrame):
    """Spending by weekday — weekend vs weekday behaviour."""
    debits = df[df["transaction_type"] == "Debit"].copy()
    debits["parsed_date"] = pd.to_datetime(debits["date"], format=DATE_FORMAT, errors="coerce")
    debits["weekday"] = debits["parsed_date"].dt.day_name()
    
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_totals = debits.groupby("weekday")["amount"].sum().reindex(order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#ff6b6b" if d in ["Saturday", "Sunday"] else "#4ecdc4" for d in order]
    day_totals.plot(kind="bar", ax=ax, color=colors, edgecolor="black")
    ax.set_title("Spending by Day of Week (red = weekend)")
    ax.set_xlabel("Day")
    ax.set_ylabel("Total Amount (₹)")
    plt.xticks(rotation=30)
    _save("spending_by_day")


# ─────────────────────────────────────────────
# 10. Outlier Detection
# ─────────────────────────────────────────────

def plot_outliers(df: pd.DataFrame):
    """Box plots for detecting spending outliers."""
    debits = df[df["transaction_type"] == "Debit"]["amount"]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].boxplot(debits, vert=True)
    axes[0].set_title("Amount Boxplot (with outliers)")
    axes[0].set_ylabel("Amount (₹)")
    
    q1, q3 = debits.quantile(0.25), debits.quantile(0.75)
    iqr = q3 - q1
    filtered = debits[(debits >= q1 - 1.5 * iqr) & (debits <= q3 + 1.5 * iqr)]
    axes[1].boxplot(filtered, vert=True)
    axes[1].set_title("Amount Boxplot (outliers removed, IQR)")
    axes[1].set_ylabel("Amount (₹)")
    
    _save("outlier_detection")


# ─────────────────────────────────────────────
# Full EDA Runner
# ─────────────────────────────────────────────

def run_eda(df: pd.DataFrame):
    """Run all EDA analyses and save plots."""
    print("📈 Running Exploratory Data Analysis...")
    
    plot_spending_distribution(df)
    plot_category_distribution(df)
    plot_merchant_distribution(df)
    plot_daily_trend(df)
    plot_monthly_trend(df)
    plot_income_vs_expense(df)
    plot_balance_history(df)
    plot_correlation_matrix(df)
    plot_day_of_week(df)
    plot_outliers(df)
    
    print(f"\n✅ EDA complete — {len(list(PLOTS_DIR.glob('*.png')))} plots saved to {PLOTS_DIR}")


if __name__ == "__main__":
    from ml.config.config import FEATURES_DATASET_PATH
    df = pd.read_csv(FEATURES_DATASET_PATH)
    run_eda(df)

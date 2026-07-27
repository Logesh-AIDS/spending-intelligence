"""
ML Pipeline Configuration
All paths, constants, and column definitions in one place.
"""
import os
from pathlib import Path

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

ROOT_DIR = Path(__file__).parent.parent.parent
ML_DIR = ROOT_DIR / "ml"
DATA_DIR = ML_DIR / "data"
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"
PLOTS_DIR = ML_DIR / "plots"

# Database
DATABASE_PATH = ROOT_DIR / "backend" / "spending.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Datasets
RAW_DATASET_PATH = DATA_DIR / "raw_transactions.csv"
VALIDATED_DATASET_PATH = DATA_DIR / "validated_transactions.csv"
FEATURES_DATASET_PATH = DATA_DIR / "features.csv"
TRAIN_DATASET_PATH = DATA_DIR / "train.csv"
VAL_DATASET_PATH = DATA_DIR / "val.csv"
TEST_DATASET_PATH = DATA_DIR / "test.csv"

# Reports
VALIDATION_REPORT_PATH = REPORTS_DIR / "validation_report.txt"
EDA_REPORT_PATH = REPORTS_DIR / "eda_report.html"

# Create directories
for d in [DATA_DIR, MODELS_DIR, REPORTS_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# Column Definitions
# ─────────────────────────────────────────────

# Raw transaction columns from DB
RAW_COLUMNS = [
    "id", "user_id", "bank", "account_number", "transaction_type",
    "amount", "date", "merchant", "upi_reference", "balance",
    "category", "created_at"
]

# Categorical columns
CATEGORICAL_COLS = ["bank", "transaction_type", "merchant", "category"]

# Numerical columns
NUMERICAL_COLS = ["amount", "balance"]

# Date columns (stored as DD/MM/YY strings in DB)
DATE_COLS = ["date"]

# Target columns for different ML tasks
# (not used in this phase — defined here for future reference)
REGRESSION_TARGETS = ["amount", "balance"]
CLASSIFICATION_TARGETS = ["transaction_type", "category"]


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

# Train/val/test split ratios
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Random seed for reproducibility
RANDOM_SEED = 42

# Date format from Canara Bank SMS parser
DATE_FORMAT = "%d/%m/%y"

# Transaction types
TRANSACTION_TYPES = ["Debit", "Credit"]

# Default categories
DEFAULT_CATEGORIES = [
    "Food", "Shopping", "Travel", "Bills", "Health",
    "Entertainment", "Education", "Salary", "Investment", "Others"
]


# ─────────────────────────────────────────────
# Validation Rules
# ─────────────────────────────────────────────

# Amount should be positive
MIN_AMOUNT = 0.01
MAX_AMOUNT = 1_000_000.0

# Balance can be negative (overdraft) but has limits
MIN_BALANCE = -100_000.0
MAX_BALANCE = 10_000_000.0

# Date validation (transactions shouldn't be in the future)
# Will be checked against current date at runtime

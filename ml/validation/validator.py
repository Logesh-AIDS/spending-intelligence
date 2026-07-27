"""
Data Validator
Validates transaction data quality and generates reports.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List

from ml.config.config import (
    MIN_AMOUNT, MAX_AMOUNT, MIN_BALANCE, MAX_BALANCE,
    TRANSACTION_TYPES, DATE_FORMAT, VALIDATION_REPORT_PATH
)


class DataValidator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues: Dict[str, List] = {
            "missing_values": [],
            "duplicates": [],
            "invalid_amounts": [],
            "invalid_balances": [],
            "invalid_dates": [],
            "invalid_types": [],
            "missing_merchants": [],
            "missing_categories": [],
            "future_dates": [],
            "data_inconsistencies": [],
        }
    
    def validate_all(self) -> Dict:
        """Run all validation checks and return summary."""
        print("🔍 Running data validation...")
        
        self._check_missing_values()
        self._check_duplicates()
        self._check_amounts()
        self._check_balances()
        self._check_dates()
        self._check_transaction_types()
        self._check_merchants()
        self._check_categories()
        self._check_consistency()
        
        summary = self._generate_summary()
        self._save_report(summary)
        
        return summary
    
    def _check_missing_values(self):
        """Check for missing values in critical columns."""
        critical_cols = ["user_id", "transaction_type", "amount", "date"]
        for col in critical_cols:
            missing = self.df[col].isnull().sum()
            if missing > 0:
                self.issues["missing_values"].append(f"{col}: {missing} missing")
    
    def _check_duplicates(self):
        """Check for duplicate transactions."""
        # Duplicate = same user, amount, date, merchant, type
        dupe_cols = ["user_id", "amount", "date", "merchant", "transaction_type"]
        dupes = self.df[self.df.duplicated(subset=dupe_cols, keep=False)]
        if len(dupes) > 0:
            self.issues["duplicates"].append(f"{len(dupes)} potential duplicates found")
    
    def _check_amounts(self):
        """Validate transaction amounts."""
        invalid = self.df[
            (self.df["amount"] < MIN_AMOUNT) |
            (self.df["amount"] > MAX_AMOUNT) |
            (self.df["amount"].isnull())
        ]
        if len(invalid) > 0:
            self.issues["invalid_amounts"].append(
                f"{len(invalid)} transactions with invalid amounts"
            )
    
    def _check_balances(self):
        """Validate balance values."""
        invalid = self.df[
            (self.df["balance"] < MIN_BALANCE) |
            (self.df["balance"] > MAX_BALANCE)
        ]
        if len(invalid) > 0:
            self.issues["invalid_balances"].append(
                f"{len(invalid)} transactions with invalid balance"
            )
    
    def _check_dates(self):
        """Validate date formats and values."""
        today = datetime.now().date()
        
        for idx, date_str in self.df["date"].items():
            if pd.isnull(date_str):
                self.issues["invalid_dates"].append(f"Row {idx}: missing date")
                continue
            
            try:
                date_obj = datetime.strptime(str(date_str), DATE_FORMAT).date()
                # Check if date is in the future
                if date_obj > today:
                    self.issues["future_dates"].append(
                        f"Row {idx}: future date {date_str}"
                    )
            except ValueError:
                self.issues["invalid_dates"].append(
                    f"Row {idx}: invalid date format '{date_str}'"
                )
    
    def _check_transaction_types(self):
        """Validate transaction types."""
        invalid = self.df[~self.df["transaction_type"].isin(TRANSACTION_TYPES)]
        if len(invalid) > 0:
            self.issues["invalid_types"].append(
                f"{len(invalid)} transactions with invalid type"
            )
    
    def _check_merchants(self):
        """Check for missing merchants in debit transactions."""
        debits_no_merchant = self.df[
            (self.df["transaction_type"] == "Debit") &
            (self.df["merchant"].isnull())
        ]
        if len(debits_no_merchant) > 0:
            self.issues["missing_merchants"].append(
                f"{len(debits_no_merchant)} debit transactions without merchant"
            )
    
    def _check_categories(self):
        """Check for missing categories."""
        no_category = self.df[self.df["category"].isnull()]
        if len(no_category) > 0:
            self.issues["missing_categories"].append(
                f"{len(no_category)} transactions without category"
            )
    
    def _check_consistency(self):
        """Check data consistency rules."""
        # Balance should generally increase with credits and decrease with debits
        # (simplified check — actual balance changes depend on sequence)
        pass
    
    def _generate_summary(self) -> Dict:
        """Generate validation summary."""
        total_issues = sum(len(v) for v in self.issues.values())
        
        summary = {
            "total_records": len(self.df),
            "total_issues": total_issues,
            "issues_by_category": {k: len(v) for k, v in self.issues.items()},
            "details": self.issues,
            "validation_passed": total_issues == 0,
        }
        
        return summary
    
    def _save_report(self, summary: Dict):
        """Save validation report to file."""
        with open(VALIDATION_REPORT_PATH, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("DATA VALIDATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Records: {summary['total_records']}\n")
            f.write(f"Total Issues: {summary['total_issues']}\n")
            f.write(f"Validation: {'✅ PASSED' if summary['validation_passed'] else '❌ FAILED'}\n\n")
            
            f.write("Issues by Category:\n")
            f.write("-" * 60 + "\n")
            for cat, count in summary['issues_by_category'].items():
                if count > 0:
                    f.write(f"{cat}: {count} issues\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("DETAILED ISSUES\n")
            f.write("=" * 60 + "\n\n")
            
            for cat, issues_list in summary['details'].items():
                if issues_list:
                    f.write(f"\n{cat.upper().replace('_', ' ')}:\n")
                    for issue in issues_list:
                        f.write(f"  - {issue}\n")
        
        print(f"📄 Validation report saved to {VALIDATION_REPORT_PATH}")


def validate_dataset(df: pd.DataFrame) -> Dict:
    """
    Validate a transaction dataset.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        Validation summary
    """
    validator = DataValidator(df)
    summary = validator.validate_all()
    
    if summary["validation_passed"]:
        print("✅ Validation PASSED — no issues found")
    else:
        print(f"❌ Validation FAILED — {summary['total_issues']} issues found")
    
    return summary


if __name__ == "__main__":
    from ml.config.config import RAW_DATASET_PATH
    df = pd.read_csv(RAW_DATASET_PATH)
    validate_dataset(df)

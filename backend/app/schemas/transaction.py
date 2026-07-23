from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    """Used when manually creating a transaction (not via SMS)."""
    bank: str
    account_number: Optional[str] = None
    transaction_type: str          # "Debit" or "Credit"
    amount: float
    date: str                      # "DD/MM/YY" format from SMS
    merchant: Optional[str] = None
    upi_reference: Optional[str] = None
    balance: Optional[float] = None
    category: Optional[str] = "Others"

    @field_validator("transaction_type")
    @classmethod
    def validate_type(cls, v):
        if v not in ("Debit", "Credit"):
            raise ValueError("transaction_type must be 'Debit' or 'Credit'")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class TransactionUpdate(BaseModel):
    """All fields optional — only send what you want to change."""
    bank: Optional[str] = None
    account_number: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    upi_reference: Optional[str] = None
    balance: Optional[float] = None
    category: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ("Debit", "Credit"):
            raise ValueError("transaction_type must be 'Debit' or 'Credit'")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class TransactionResponse(BaseModel):
    """What we return to the client — never expose user_id internals."""
    id: int
    bank: str
    account_number: Optional[str]
    transaction_type: str
    amount: float
    date: str
    merchant: Optional[str]
    upi_reference: Optional[str]
    balance: Optional[float]
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedTransactions(BaseModel):
    """Standard paginated list response."""
    total_records: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    transactions: list[TransactionResponse]

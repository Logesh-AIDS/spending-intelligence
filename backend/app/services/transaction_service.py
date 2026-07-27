import re
from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, transaction_id: int, user_id: int) -> Transaction:
    """
    Fetch a transaction by id that belongs to this user.
    Raises 404 if not found, which also covers the case where the
    transaction belongs to a different user (ownership enforced silently).
    """
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
        .first()
    )
    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    return txn


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def _sanitize(value: str | None) -> str | None:
    """Strip HTML tags from string fields to prevent XSS storage."""
    if value is None:
        return None
    return re.sub(r'<[^>]+>', '', str(value)).strip()


def create_transaction(db: Session, payload: TransactionCreate, user_id: int) -> Transaction:
    txn = Transaction(
        user_id=user_id,
        bank=_sanitize(payload.bank),
        account_number=_sanitize(payload.account_number),
        transaction_type=payload.transaction_type,
        amount=payload.amount,
        date=payload.date,
        merchant=_sanitize(payload.merchant),
        upi_reference=_sanitize(payload.upi_reference),
        balance=payload.balance,
        category=_sanitize(payload.category) or "Others",
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ---------------------------------------------------------------------------
# READ LIST  (filtering + pagination + sorting)
# ---------------------------------------------------------------------------

SORT_COLUMNS = {
    "date": Transaction.date,
    "amount": Transaction.amount,
    "merchant": Transaction.merchant,
    "created_at": Transaction.created_at,
}


def get_transactions(
    db: Session,
    user_id: int,
    # --- pagination ---
    page: int = 1,
    page_size: int = 20,
    # --- filters ---
    transaction_type: Optional[str] = None,
    merchant: Optional[str] = None,
    bank: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    # --- sorting ---
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> dict:

    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    # --- apply filters ---
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    if merchant:
        query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))

    if bank:
        query = query.filter(Transaction.bank.ilike(f"%{bank}%"))

    if category:
        query = query.filter(Transaction.category == category)

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    # date stored as "DD/MM/YY" string — string comparison works for same-format dates
    if date_from:
        query = query.filter(Transaction.date >= date_from)

    if date_to:
        query = query.filter(Transaction.date <= date_to)

    # fuzzy search across merchant, bank, upi_reference
    if search:
        term = f"%{search}%"
        query = query.filter(
            Transaction.merchant.ilike(term)
            | Transaction.bank.ilike(term)
            | Transaction.upi_reference.ilike(term)
        )

    # --- sorting ---
    col = SORT_COLUMNS.get(sort_by, Transaction.created_at)
    query = query.order_by(desc(col) if sort_order == "desc" else asc(col))

    # --- pagination ---
    total_records = query.count()
    total_pages = ceil(total_records / page_size) if total_records > 0 else 1
    offset = (page - 1) * page_size
    transactions = query.offset(offset).limit(page_size).all()

    return {
        "total_records": total_records,
        "current_page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "transactions": transactions,
    }


# ---------------------------------------------------------------------------
# READ SINGLE
# ---------------------------------------------------------------------------

def get_transaction_by_id(db: Session, transaction_id: int, user_id: int) -> Transaction:
    return _get_or_404(db, transaction_id, user_id)


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_transaction(
    db: Session,
    transaction_id: int,
    payload: TransactionUpdate,
    user_id: int
) -> Transaction:
    txn = _get_or_404(db, transaction_id, user_id)

    # Only update fields that were actually sent in the request
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_transaction(db: Session, transaction_id: int, user_id: int) -> dict:
    txn = _get_or_404(db, transaction_id, user_id)
    db.delete(txn)
    db.commit()
    return {"message": f"Transaction {transaction_id} deleted successfully"}

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    PaginatedTransactions,
)
from app.services import transaction_service

router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["Transactions"]
)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new transaction for the authenticated user."""
    return transaction_service.create_transaction(db, payload, current_user.id)


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
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
    # ---
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List transactions for the authenticated user.
    Supports filtering, pagination, and sorting.
    """
    return transaction_service.get_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        transaction_type=transaction_type,
        merchant=merchant,
        bank=bank,
        category=category,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single transaction by ID."""
    return transaction_service.get_transaction_by_id(db, transaction_id, current_user.id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a transaction.
    Only fields included in the request will be updated.
    """
    return transaction_service.update_transaction(db, transaction_id, payload, current_user.id)


@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a transaction."""
    return transaction_service.delete_transaction(db, transaction_id, current_user.id)

"""
Bank Statement Upload API
POST /api/v1/statements/upload  — accepts a PDF, parses it, saves transactions.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.core.dependencies import get_current_user
from app.parsers.pdf_parser import parse_bank_statement_pdf
from app.schemas.transaction import TransactionResponse

router = APIRouter(
    prefix="/api/v1/statements",
    tags=["Statements"],
)

_MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a bank statement PDF and import all transactions",
)
async def upload_statement(
    file: UploadFile = File(..., description="Bank statement PDF file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a PDF bank statement (Canara Bank supported).

    - Parses all transactions from the PDF table.
    - Skips duplicates already stored for this user (matched on date + amount + type).
    - Returns a summary: total parsed, imported, skipped.
    """
    # ── Validate file type ────────────────────────────────────────
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    # ── Read and size-check ───────────────────────────────────────
    file_bytes = await file.read()
    if len(file_bytes) > _MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF is too large. Maximum allowed size is 10 MB.",
        )

    # ── Parse PDF ─────────────────────────────────────────────────
    try:
        parsed = parse_bank_statement_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read PDF: {e}",
        )

    # ── Deduplicate against existing user transactions ────────────
    # Load existing (date, amount, transaction_type) tuples for this user
    existing = db.query(
        Transaction.date,
        Transaction.amount,
        Transaction.transaction_type,
    ).filter(Transaction.user_id == current_user.id).all()

    existing_keys = {(r.date, r.amount, r.transaction_type) for r in existing}

    # ── Bulk insert new transactions ──────────────────────────────
    imported: List[Transaction] = []
    skipped = 0

    for txn_data in parsed:
        key = (txn_data["date"], txn_data["amount"], txn_data["transaction_type"])
        if key in existing_keys:
            skipped += 1
            continue

        txn = Transaction(
            user_id=current_user.id,
            bank=txn_data.get("bank", "Unknown"),
            account_number=txn_data.get("account_number"),
            transaction_type=txn_data["transaction_type"],
            amount=txn_data["amount"],
            date=txn_data["date"],
            merchant=txn_data.get("merchant"),
            upi_reference=txn_data.get("upi_reference"),
            balance=txn_data.get("balance"),
            category=txn_data.get("category", "Others"),
        )
        db.add(txn)
        imported.append(txn)
        # Add to seen set to avoid double-inserting within same upload
        existing_keys.add(key)

    db.commit()

    return {
        "message": f"Statement imported successfully.",
        "total_parsed": len(parsed),
        "imported": len(imported),
        "skipped_duplicates": skipped,
    }

"""
Bank Statement Upload API
POST /api/v1/statements/upload  — accepts a PDF, parses it, saves transactions.
POST /api/v1/statements/debug   — returns raw extracted text+tables for diagnosis.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import io

import pdfplumber

from app.database.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.core.dependencies import get_current_user
from app.parsers.pdf_parser import parse_bank_statement_pdf

router = APIRouter(
    prefix="/api/v1/statements",
    tags=["Statements"],
)

_MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Debug endpoint — shows raw pdfplumber output ──────────────────
@router.post("/debug", summary="Show raw PDF extraction for diagnosis")
async def debug_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Returns the first 3 pages of raw text + table rows for debugging."""
    file_bytes = await file.read()
    result = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages[:5]):  # first 5 pages
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            result.append({
                "page": i + 1,
                "text_lines": text.splitlines()[:40],  # first 40 lines
                "tables": [
                    {"rows": t[:10]} for t in tables  # first 10 rows per table
                ],
            })
    return {"pages": result}


# ── Upload endpoint ────────────────────────────────────────────────
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
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > _MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="PDF too large. Max 10 MB.")

    try:
        parsed = parse_bank_statement_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {e}")

    existing = db.query(
        Transaction.date, Transaction.amount, Transaction.transaction_type,
    ).filter(Transaction.user_id == current_user.id).all()
    existing_keys = {(r.date, r.amount, r.transaction_type) for r in existing}

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
        existing_keys.add(key)

    db.commit()

    return {
        "message": "Statement imported successfully.",
        "total_parsed": len(parsed),
        "imported": len(imported),
        "skipped_duplicates": skipped,
    }

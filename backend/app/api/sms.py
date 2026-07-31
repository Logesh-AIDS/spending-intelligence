from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.sms import SMSRequest
from app.parsers.sms_parser import parse_sms
from app.database.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/sms",
    tags=["SMS"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def receive_sms(
    request: SMSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        transaction = parse_sms(request.raw_sms)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Reject if critical fields are missing
    if not transaction.get("transaction_type") or not transaction.get("amount"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract transaction type or amount from SMS"
        )

    db_transaction = Transaction(
        user_id=current_user.id,
        bank=transaction["bank"],
        account_number=transaction.get("account_number"),
        transaction_type=transaction["transaction_type"],
        amount=transaction["amount"],
        date=transaction.get("date", ""),
        merchant=transaction.get("merchant"),
        upi_reference=transaction.get("upi_reference"),
        balance=transaction.get("balance"),
        category="Others",
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return {
        "message": "Transaction saved successfully",
        "transaction": {
            "id": db_transaction.id,
            "bank": db_transaction.bank,
            "amount": db_transaction.amount,
            "transaction_type": db_transaction.transaction_type,
            "merchant": db_transaction.merchant,
            "date": db_transaction.date,
        }
    }

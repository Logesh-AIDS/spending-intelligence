from fastapi import APIRouter
from app.schemas.sms import SMSRequest
from app.parsers.sms_parser import parse_sms

router = APIRouter(
    prefix="/api/v1/sms",
    tags=["SMS"]
)


@router.post("/")
def receive_sms(request: SMSRequest):

    transaction = parse_sms(request.raw_sms)

    return {
        "message": "SMS received",
        "transaction": transaction
    }
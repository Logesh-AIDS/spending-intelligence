from pydantic import BaseModel


class SMSRequest(BaseModel):
    raw_sms: str
from app.parsers.canara_parser import parse_canara_sms


def parse_sms(raw_sms: str):

    if "CanaraBank" in raw_sms:
        return parse_canara_sms(raw_sms)

    raise ValueError("Unsupported bank")
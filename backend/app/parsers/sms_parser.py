from app.parsers.canara_parser import parse_canara_sms


# All known Canara Bank sender IDs
CANARA_SENDERS = [
    "canarabank", "canara bank", "canbnk", "canbank",
    "ax-canbnk", "ad-canbnk", "vk-canbnk", "tm-canbnk",
    "-canarabank", "-canara bank"
]


def parse_sms(raw_sms: str) -> dict:
    """
    Dispatch SMS to the correct bank parser.
    Checks both SMS body and common Canara Bank patterns.
    """
    raw_lower = raw_sms.lower()

    # Check for Canara Bank indicators
    is_canara = (
        any(sender in raw_lower for sender in CANARA_SENDERS) or
        # Body clues when sender ID not in message body
        ("acct xxx" in raw_lower and ("dr." in raw_sms or "cr." in raw_sms or "credited" in raw_lower)) or
        ("a/c xx" in raw_lower and "upi ref" in raw_lower) or
        ("blockupi to 9901771222" in raw_lower) or
        ("dial 1930 to report cyber fraud - canara" in raw_lower)
    )

    if is_canara:
        return parse_canara_sms(raw_sms)

    raise ValueError(f"Unsupported bank SMS format")

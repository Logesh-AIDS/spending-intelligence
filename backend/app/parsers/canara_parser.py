import re


def parse_canara_sms(raw_sms: str):

    # -------------------------
    # Account Number
    # Example: Acct XXX695
    # -------------------------
    account_match = re.search(r"Acct\s+(\w+)", raw_sms)
    account_number = account_match.group(1) if account_match else None

    # -------------------------
    # Transaction Type
    # Dr. -> Debit
    # Cr. -> Credit
    # -------------------------
    transaction_type = None

    if "Dr." in raw_sms:
        transaction_type = "Debit"
    elif "Cr." in raw_sms:
        transaction_type = "Credit"

    # -------------------------
    # Amount
    # Example:
    # Dr. INR 10.00
    # -------------------------
    amount_match = re.search(
        r"(?:Dr|Cr)\.\s*INR\s*([\d,]+\.\d+)",
        raw_sms
    )

    amount = None
    if amount_match:
        amount = float(amount_match.group(1).replace(",", ""))

    # -------------------------
    # Date
    # Example:
    # on 22/07/26
    # -------------------------
    date_match = re.search(
        r"on\s+(\d{2}/\d{2}/\d{2})",
        raw_sms
    )

    date = date_match.group(1) if date_match else None

    # -------------------------
    # Merchant / Receiver
    # Example:
    # to DHARSHIKA D;
    # -------------------------
    merchant_match = re.search(
        r"to\s+(.+?);",
        raw_sms
    )

    merchant = merchant_match.group(1).strip() if merchant_match else None

    # -------------------------
    # UPI Reference
    # Example:
    # UPI: 620363833776;
    # -------------------------
    upi_match = re.search(
        r"UPI:\s*(\d+)",
        raw_sms
    )

    upi_reference = upi_match.group(1) if upi_match else None

    # -------------------------
    # Balance
    # Example:
    # Bal INR 3,446.02
    # -------------------------
    balance_match = re.search(
        r"Bal\s+INR\s+([\d,]+\.\d+)",
        raw_sms
    )

    balance = None

    if balance_match:
        balance = float(balance_match.group(1).replace(",", ""))

    # -------------------------
    # Bank
    # -------------------------
    bank = "CanaraBank"

    return {
        "bank": bank,
        "account_number": account_number,
        "transaction_type": transaction_type,
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "upi_reference": upi_reference,
        "balance": balance
    }
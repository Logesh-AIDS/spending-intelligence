import re
from datetime import datetime


def parse_canara_sms(raw_sms: str) -> dict:
    """
    Parses all known Canara Bank SMS formats:

    Format 1 (UPI alert):
      Dear Customer, Acct XXX695 Dr. INR 50.00 on 18/07/26 to SRI CUMIN SE; UPI: 619915762426; Bal INR 4,123.02.

    Format 2 (Rs. paid):
      Rs.90.00 paid thru A/C XX9695 on 21-6-26 13:04:36 to Barkath S, UPI Ref 653874040961.

    Format 3 (DEBITED amount):
      An amount of INR 50.00 has been DEBITED to your account XXX695 on 19/06/2026. Total Avail.bal INR 903.17.

    Format 4 (credited with):
      Dear Customer, Acct XXX695 credited with INR 63.00 on 29/07/26 from VIBIN KUMAR; UPI:657644484581; Bal INR 1,264.52
    """

    # ── Transaction Type ─────────────────────────────────────────────────────
    transaction_type = None
    raw_lower = raw_sms.lower()

    if "Dr." in raw_sms or "debited" in raw_lower or "paid thru" in raw_lower or "has been debit" in raw_lower:
        transaction_type = "Debit"
    elif "Cr." in raw_sms or "credited" in raw_lower:
        transaction_type = "Credit"

    # ── Amount ───────────────────────────────────────────────────────────────
    amount = None

    # Format 1 & 4: Dr. INR 50.00 or Cr. INR 63.00
    m = re.search(r"(?:Dr|Cr)\.\s*INR\s*([\d,]+\.?\d*)", raw_sms)
    if m:
        amount = float(m.group(1).replace(",", ""))

    # Format 2: Rs.90.00 paid
    if amount is None:
        m = re.search(r"Rs\.?\s*([\d,]+\.?\d*)\s+paid", raw_sms, re.IGNORECASE)
        if m:
            amount = float(m.group(1).replace(",", ""))

    # Format 3: amount of INR 50.00 has been DEBITED
    if amount is None:
        m = re.search(r"amount of\s+INR\s+([\d,]+\.?\d*)", raw_sms, re.IGNORECASE)
        if m:
            amount = float(m.group(1).replace(",", ""))

    # Fallback: any INR amount
    if amount is None:
        m = re.search(r"INR\s*([\d,]+\.?\d*)", raw_sms, re.IGNORECASE)
        if m:
            amount = float(m.group(1).replace(",", ""))

    # ── Account Number ───────────────────────────────────────────────────────
    account_number = None

    # Format 1 & 4: Acct XXX695
    m = re.search(r"Acct\s+(\w+)", raw_sms)
    if m:
        account_number = m.group(1)

    # Format 2: A/C XX9695
    if account_number is None:
        m = re.search(r"A/C\s+(\w+)", raw_sms)
        if m:
            account_number = m.group(1)

    # Format 3: account XXX695
    if account_number is None:
        m = re.search(r"account\s+(\w+)", raw_sms, re.IGNORECASE)
        if m:
            account_number = m.group(1)

    # ── Date ─────────────────────────────────────────────────────────────────
    date = None

    # Format 1 & 4: on 18/07/26
    m = re.search(r"on\s+(\d{2}/\d{2}/\d{2})\b", raw_sms)
    if m:
        date = m.group(1)

    # Format 2: on 21-6-26 (may have time after)
    if date is None:
        m = re.search(r"on\s+(\d{1,2}-\d{1,2}-\d{2})", raw_sms)
        if m:
            raw_date = m.group(1)
            try:
                d = datetime.strptime(raw_date, "%d-%m-%y")
                date = d.strftime("%d/%m/%y")
            except ValueError:
                date = raw_date

    # Format 3: on 19/06/2026 (4-digit year)
    if date is None:
        m = re.search(r"on\s+(\d{2}/\d{2}/\d{4})", raw_sms)
        if m:
            try:
                d = datetime.strptime(m.group(1), "%d/%m/%Y")
                date = d.strftime("%d/%m/%y")
            except ValueError:
                date = m.group(1)

    # ── Merchant ─────────────────────────────────────────────────────────────
    merchant = None

    # Format 1: to MERCHANT NAME;
    m = re.search(r"\bto\s+([^;]+);", raw_sms)
    if m:
        merchant = m.group(1).strip()

    # Format 4: from MERCHANT NAME;
    if merchant is None:
        m = re.search(r"\bfrom\s+([^;]+);", raw_sms)
        if m:
            merchant = m.group(1).strip()

    # Format 2: to Barkath S,
    if merchant is None:
        m = re.search(r"\bto\s+([^,]+),\s+UPI", raw_sms)
        if m:
            merchant = m.group(1).strip()

    # Clean up merchant — remove trailing punctuation
    if merchant:
        merchant = re.sub(r"[.;,]+$", "", merchant).strip()

    # ── UPI Reference ────────────────────────────────────────────────────────
    upi_reference = None

    # Format 1 & 4: UPI: 619915762426
    m = re.search(r"UPI:?\s*(\d+)", raw_sms)
    if m:
        upi_reference = m.group(1)

    # Format 2: UPI Ref 653874040961
    if upi_reference is None:
        m = re.search(r"UPI\s+Ref\s+(\d+)", raw_sms)
        if m:
            upi_reference = m.group(1)

    # ── Balance ──────────────────────────────────────────────────────────────
    balance = None

    # Format 1 & 4: Bal INR 4,123.02
    m = re.search(r"Bal\s+INR\s+([\d,]+\.?\d*)", raw_sms, re.IGNORECASE)
    if m:
        balance = float(m.group(1).replace(",", ""))

    # Format 3: Total Avail.bal INR 903.17
    if balance is None:
        m = re.search(r"(?:Avail\.?bal|balance)\s+INR\s+([\d,]+\.?\d*)", raw_sms, re.IGNORECASE)
        if m:
            balance = float(m.group(1).replace(",", ""))

    return {
        "bank": "CanaraBank",
        "account_number": account_number,
        "transaction_type": transaction_type,
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "upi_reference": upi_reference,
        "balance": balance,
    }

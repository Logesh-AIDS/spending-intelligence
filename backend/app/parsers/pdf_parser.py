"""
PDF Bank Statement Parser — Canara Bank ePassbook format
Each transaction block looks like:

    08-08-2026
    UPI/DR/658675640481/JAGATH EES/CNRB/**279-2@OKHDFCBANK/UPI//AXI...
    Chq: 658675640481
    70.00  611.72

    09-08-2026
    UPI/CR/127651094045/ALAVANDAN/KVBL/**ASS09@OKHDFC...
    Chq: 127651094045
    500.00  536.97

Structure:
- Line 1   : date  (DD-MM-YYYY)
- Lines 2-N: particulars (multi-line, ends with "Chq: <number>" or just the amounts)
- Last line : <amount>  <balance>   (one or two numbers)
  OR two amounts on separate lines for Deposits vs Withdrawals column
"""

import re
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

import pdfplumber


# ── Date parsing ──────────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^(\d{2}-\d{2}-\d{4})$")

def _parse_date(raw: str) -> Optional[str]:
    raw = raw.strip()
    try:
        return datetime.strptime(raw, "%d-%m-%Y").strftime("%d/%m/%y")
    except ValueError:
        pass
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%d/%m/%y")
        except ValueError:
            continue
    return None


# ── Amount parsing ────────────────────────────────────────────────────────────

_AMOUNT_RE = re.compile(r"^[\d,]+\.\d{2}$")

def _to_float(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


# ── Merchant / category extraction ───────────────────────────────────────────

def _extract_merchant(particulars: str) -> Optional[str]:
    """
    Extract human-readable merchant from Canara Bank UPI narration.
    Formats seen:
      UPI/DR/<ref>/<MERCHANT>/<bank>/**<vpa>/<extra>
      UPI/CR/<ref>/<MERCHANT>/<bank>/**<vpa>/<extra>
      APY CONTRI FOR(...)
      NEFT/IMPS/RTGS patterns
    """
    p = particulars.strip()

    # UPI pattern: UPI/DR or CR / ref / merchant / ...
    m = re.match(
        r"UPI/(?:DR|CR)/\d+/([^/\n]+)/",
        p, re.IGNORECASE
    )
    if m:
        merchant = m.group(1).strip()
        # Clean up split words like "JAGATH\nEES" → "JAGATH EES"
        merchant = re.sub(r"\s+", " ", merchant)
        return merchant

    # APY contribution
    if p.upper().startswith("APY CONTRI"):
        return "APY Contribution"

    # NEFT / IMPS / RTGS
    m = re.match(r"(NEFT|IMPS|RTGS)[/ -]", p, re.IGNORECASE)
    if m:
        # Try to grab the payee name after the ref number
        m2 = re.search(r"(?:NEFT|IMPS|RTGS)[/ -]\w+[/ -]([A-Za-z][A-Za-z0-9 ]+)", p, re.IGNORECASE)
        if m2:
            return m2.group(1).strip()
        return m.group(1).upper() + " Transfer"

    # Fallback: first 50 chars of particulars
    return p[:50].strip() if p else None


def _infer_category(merchant: Optional[str], particulars: str) -> str:
    text = " ".join(filter(None, [merchant, particulars])).lower()

    rules = [
        (["zomato", "swiggy", "hotel", "restaurant", "cafe", "food", "biryani",
          "pizza", "burger", "dine", "eat", "kitchen", "canteen", "amman mess",
          "amman tea", "sri cumin", "vks resta", "valli hot", "madras ba",
          "tea time", "famous ca", "kings bak"], "Food"),
        (["amazon", "flipkart", "myntra", "ajio", "nykaa", "shop", "mart",
          "store", "purchase", "meesho", "reliance", "bigbasket", "blinkit",
          "vsv trade", "v s v"], "Shopping"),
        (["uber", "ola", "rapido", "irctc", "railway", "air", "flight",
          "bus", "metro", "toll", "petrol", "fuel", "cab", "nps petro",
          "airtel", "airp"], "Travel"),
        (["electricity", "water", "gas", "broadband", "internet", "mobile",
          "recharge", "jio", "vi ", "bsnl", "bill", "insurance",
          "lic ", "postpaid", "sbipmopad", "google pl", "apy contri",
          "sbibhim", "sbipmop"], "Bills"),
        (["hospital", "pharmacy", "medical", "clinic", "doctor", "apollo",
          "health", "medicine", "lab", "diagnostic"], "Health"),
        (["netflix", "prime", "hotstar", "spotify", "youtube", "game",
          "cinema", "movie", "entertainment", "pvr", "inox"], "Entertainment"),
        (["school", "college", "university", "tuition", "course", "udemy",
          "coursera", "education", "fee", "exam"], "Education"),
        (["salary", "payroll", "wages", "stipend", "neft cr", "imps cr",
          "sks poly", "skspoly"], "Salary"),
    ]

    for keywords, category in rules:
        if any(kw in text for kw in keywords):
            return category

    return "Others"


def _extract_upi_ref(particulars: str, chq: str) -> Optional[str]:
    # Chq line is most reliable for UPI ref
    if chq and re.match(r"\d{9,}", chq):
        return chq
    # Fallback: ref embedded in UPI string
    m = re.match(r"UPI/(?:DR|CR)/(\d+)/", particulars, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


# ── Core page text parser ─────────────────────────────────────────────────────

# Line that is purely one or two money amounts: e.g. "70.00  611.72" or "500.00"
_AMOUNTS_LINE_RE = re.compile(
    r"^([\d,]+\.\d{2})(?:\s+([\d,]+\.\d{2}))?$"
)
# "Opening Balance 681.72" or "Closing Balance 186.15"
_BALANCE_LABEL_RE = re.compile(
    r"^(?:Opening|Closing)\s+Balance\s+([\d,]+\.\d{2})$", re.IGNORECASE
)
# "Chq: 658675640481"
_CHQ_RE = re.compile(r"^Chq:\s*(\S*)$", re.IGNORECASE)
# Column header row
_HEADER_RE = re.compile(
    r"Date\s+Particulars\s+Deposits\s+Withdrawals\s+Balance", re.IGNORECASE
)
# Page footer "page N"
_PAGE_RE = re.compile(r"^page\s+\d+$", re.IGNORECASE)


def _parse_page_text(text: str, account_number: Optional[str]) -> List[Dict[str, Any]]:
    """Parse one page of raw text into transaction dicts."""
    lines = [l.rstrip() for l in text.splitlines()]
    transactions: List[Dict[str, Any]] = []

    i = 0
    n = len(lines)

    # Current transaction state
    cur_date: Optional[str] = None
    cur_particulars: List[str] = []
    cur_chq: Optional[str] = None

    def flush(amount: float, balance: Optional[float], is_deposit: bool):
        """Save accumulated state as one transaction."""
        nonlocal cur_date, cur_particulars, cur_chq
        if not cur_date or not amount:
            return

        particulars = " ".join(cur_particulars).strip()
        # Determine type from UPI/DR or UPI/CR prefix
        if re.match(r"UPI/CR/", particulars, re.IGNORECASE):
            txn_type = "Credit"
        elif re.match(r"UPI/DR/", particulars, re.IGNORECASE):
            txn_type = "Debit"
        else:
            txn_type = "Credit" if is_deposit else "Debit"

        merchant = _extract_merchant(particulars)
        category = _infer_category(merchant, particulars)
        upi_ref = _extract_upi_ref(particulars, cur_chq or "")

        transactions.append({
            "bank": "CanaraBank",
            "account_number": account_number,
            "transaction_type": txn_type,
            "amount": amount,
            "date": cur_date,
            "merchant": merchant,
            "upi_reference": upi_ref,
            "balance": balance,
            "category": category,
            "particulars": particulars,  # kept for debugging
        })

        cur_date = None
        cur_particulars = []
        cur_chq = None

    while i < n:
        line = lines[i].strip()

        # Skip blank, header, footer lines
        if not line or _HEADER_RE.match(line) or _PAGE_RE.match(line):
            i += 1
            continue

        # Skip disclaimer / end-of-statement text
        if any(kw in line.upper() for kw in [
            "DISCLAIMER", "UNLESS THE CONSTITUENT", "BEWARE OF PHISHING",
            "IMB USERS", "CHANGE IN THE ADDRESS", "DO NOT SHARE",
            "OMBUDSMAN", "COMPUTER OUTPUT", "END OF STATEMENT",
            "BANGALORE", "E-MAIL", "ARE YOU A MERCHANT"
        ]):
            i += 1
            continue

        # Opening/Closing balance lines — skip
        if _BALANCE_LABEL_RE.match(line):
            i += 1
            continue

        # Date line — starts a new transaction block
        if _DATE_RE.match(line):
            # If we have a pending transaction without amounts yet,
            # look ahead one line for the amounts before starting new block
            cur_date = _parse_date(line)
            cur_particulars = []
            cur_chq = None
            i += 1
            continue

        # Chq line
        chq_m = _CHQ_RE.match(line)
        if chq_m:
            cur_chq = chq_m.group(1)
            i += 1
            continue

        # Amounts line — closes the current transaction
        amt_m = _AMOUNTS_LINE_RE.match(line)
        if amt_m and cur_date:
            a1 = _to_float(amt_m.group(1))
            a2 = _to_float(amt_m.group(2)) if amt_m.group(2) else None

            # Canara statement: single number = amount (no balance on this line)
            # Two numbers: could be (amount, balance) or (deposit, withdrawal)
            # Since this is a passbook, columns are: Deposits | Withdrawals | Balance
            # The amount line typically has exactly ONE amount (deposit OR withdrawal)
            # and ONE balance. If only one number, it's the amount; balance is on next
            # line or missing.
            # Heuristic: if two numbers, second is balance.
            # Determine debit/credit from particulars.
            amount = a1
            balance = a2

            # Decide credit vs debit from particulars
            particulars_str = " ".join(cur_particulars)
            is_deposit = bool(re.match(r"UPI/CR/", particulars_str, re.IGNORECASE))

            flush(amount, balance, is_deposit)
            i += 1
            continue

        # Otherwise it's a particulars continuation line
        if cur_date is not None and line:
            cur_particulars.append(line)

        i += 1

    return transactions


# ── Account number extraction ─────────────────────────────────────────────────

def _extract_account_number(text: str) -> Optional[str]:
    # "Statement for A/c XXXXXXXX9695"
    m = re.search(r"A/c\s+([X0-9]+)", text)
    if m:
        return m.group(1)
    m = re.search(r"account\s*(?:no|number)[.:\s]+([0-9X]{6,20})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


# ── Public entry point ────────────────────────────────────────────────────────

def parse_bank_statement_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse a Canara Bank ePassbook PDF.
    Returns list of transaction dicts with keys:
        bank, account_number, transaction_type, amount, date,
        merchant, upi_reference, balance, category
    Raises ValueError if nothing parsed.
    """
    all_transactions: List[Dict[str, Any]] = []
    account_number: Optional[str] = None

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""

            if account_number is None:
                account_number = _extract_account_number(text)

            page_txns = _parse_page_text(text, account_number)
            all_transactions.extend(page_txns)

    # Deduplicate by UPI ref (most reliable) then by date+amount+type
    seen_refs: set = set()
    seen_keys: set = set()
    unique: List[Dict[str, Any]] = []

    for t in all_transactions:
        ref = t.get("upi_reference")
        key = (t["date"], t["amount"], t["transaction_type"])

        if ref and ref in seen_refs:
            continue
        if key in seen_keys:
            continue

        if ref:
            seen_refs.add(ref)
        seen_keys.add(key)

        # Remove internal debug field before returning
        t.pop("particulars", None)
        unique.append(t)

    if not unique:
        raise ValueError(
            "No transactions found in the PDF. "
            "Please upload a Canara Bank ePassbook statement."
        )

    return unique

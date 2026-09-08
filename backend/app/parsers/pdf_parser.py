"""
PDF Bank Statement Parser
Supports: Canara Bank statements (table-based and text-based formats)
Returns a list of transaction dicts compatible with TransactionCreate schema.
"""

import re
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

import pdfplumber


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_amount(raw: str) -> Optional[float]:
    """Convert '1,23,456.78' or '1234.56' to float. Returns None on failure."""
    if not raw:
        return None
    cleaned = re.sub(r"[^\d.]", "", raw.strip())
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _parse_date(raw: str) -> Optional[str]:
    """
    Normalise various date formats to DD/MM/YY.
    Handles: DD/MM/YYYY, DD-MM-YYYY, DD/MM/YY, DD-MM-YY, DD MMM YYYY, DD-MMM-YY
    """
    if not raw:
        return None
    raw = raw.strip()

    formats = [
        ("%d/%m/%Y", "%d/%m/%y"),
        ("%d-%m-%Y", "%d/%m/%y"),
        ("%d/%m/%y", "%d/%m/%y"),
        ("%d-%m-%y", "%d/%m/%y"),
        ("%d %b %Y", "%d/%m/%y"),
        ("%d-%b-%Y", "%d/%m/%y"),
        ("%d %b %y",  "%d/%m/%y"),
        ("%d-%b-%y",  "%d/%m/%y"),
        ("%d/%b/%Y", "%d/%m/%y"),
        ("%d/%b/%y", "%d/%m/%y"),
    ]
    for in_fmt, out_fmt in formats:
        try:
            return datetime.strptime(raw, in_fmt).strftime(out_fmt)
        except ValueError:
            continue
    return None


def _infer_category(merchant: Optional[str], narration: Optional[str]) -> str:
    """Rule-based category assignment from merchant/narration text."""
    text = " ".join(filter(None, [merchant, narration])).lower()

    rules = [
        (["zomato", "swiggy", "hotel", "restaurant", "cafe", "food", "biryani",
          "pizza", "burger", "dine", "eat", "kitchen", "canteen"], "Food"),
        (["amazon", "flipkart", "myntra", "ajio", "nykaa", "shop", "mart",
          "store", "purchase", "meesho", "reliance", "bigbasket", "blinkit"], "Shopping"),
        (["uber", "ola", "rapido", "irctc", "railway", "air", "flight",
          "bus", "metro", "toll", "petrol", "fuel", "cab"], "Travel"),
        (["electricity", "water", "gas", "broadband", "internet", "mobile",
          "recharge", "jio", "airtel", "vi ", "bsnl", "bill", "insurance",
          "lic ", "postpaid"], "Bills"),
        (["hospital", "pharmacy", "medical", "clinic", "doctor", "apollo",
          "health", "medicine", "lab", "diagnostic"], "Health"),
        (["netflix", "prime", "hotstar", "spotify", "youtube", "game",
          "cinema", "movie", "entertainment", "pvr", "inox"], "Entertainment"),
        (["school", "college", "university", "tuition", "course", "udemy",
          "coursera", "education", "fee", "exam"], "Education"),
        (["salary", "payroll", "wages", "stipend", "neft cr", "imps cr"], "Salary"),
    ]

    for keywords, category in rules:
        if any(kw in text for kw in keywords):
            return category

    return "Others"


# ── Canara Bank PDF Parser ────────────────────────────────────────────────────

# Column header aliases used in different statement versions
_CANARA_DATE_HEADERS    = {"date", "txn date", "transaction date", "value date"}
_CANARA_NARR_HEADERS    = {"narration", "particulars", "description", "details", "remarks"}
_CANARA_REF_HEADERS     = {"ref no", "ref no.", "chq/ref no", "reference", "upi ref", "transaction id"}
_CANARA_DEBIT_HEADERS   = {"debit", "withdrawal", "dr", "debit(dr)", "withdrawal(dr)"}
_CANARA_CREDIT_HEADERS  = {"credit", "deposit", "cr", "credit(cr)", "deposit(cr)"}
_CANARA_BALANCE_HEADERS = {"balance", "closing balance", "avail bal", "bal"}


def _match_header(cell: str, aliases: set) -> bool:
    return cell.strip().lower() in aliases


def _find_column_indices(headers: List[str]) -> Dict[str, int]:
    """Map semantic column names to their index in the header row."""
    mapping = {}
    for i, h in enumerate(headers):
        hl = h.strip().lower()
        if hl in _CANARA_DATE_HEADERS:
            mapping.setdefault("date", i)
        elif hl in _CANARA_NARR_HEADERS:
            mapping.setdefault("narration", i)
        elif hl in _CANARA_REF_HEADERS:
            mapping.setdefault("ref", i)
        elif hl in _CANARA_DEBIT_HEADERS:
            mapping.setdefault("debit", i)
        elif hl in _CANARA_CREDIT_HEADERS:
            mapping.setdefault("credit", i)
        elif hl in _CANARA_BALANCE_HEADERS:
            mapping.setdefault("balance", i)
    return mapping


def _parse_table_row(row: List[str], col: Dict[str, int], account_number: Optional[str]) -> Optional[Dict[str, Any]]:
    """Convert one table row to a transaction dict. Returns None if row is invalid."""

    def get(key: str) -> str:
        idx = col.get(key)
        if idx is None or idx >= len(row):
            return ""
        return (row[idx] or "").strip()

    raw_date  = get("date")
    narration = get("narration")
    ref       = get("ref")
    debit_raw = get("debit")
    credit_raw = get("credit")
    balance_raw = get("balance")

    # Skip header repeat rows and empty rows
    if not raw_date or raw_date.lower() in _CANARA_DATE_HEADERS:
        return None

    date = _parse_date(raw_date)
    if not date:
        return None

    debit  = _clean_amount(debit_raw)
    credit = _clean_amount(credit_raw)

    # At least one side must have a non-zero value
    if not debit and not credit:
        return None
    if debit and debit <= 0 and credit and credit <= 0:
        return None

    if debit and debit > 0:
        transaction_type = "Debit"
        amount = debit
    else:
        transaction_type = "Credit"
        amount = credit

    balance = _clean_amount(balance_raw)

    # Extract UPI reference from narration or ref column
    upi_ref = None
    upi_match = re.search(r"(?:upi[/ -]?ref[: ]?|upi:?)(\d{8,})", narration, re.IGNORECASE)
    if upi_match:
        upi_ref = upi_match.group(1)
    elif ref and re.match(r"\d{8,}", ref.replace(" ", "")):
        upi_ref = re.sub(r"\D", "", ref)

    # Extract merchant from narration
    merchant = _extract_merchant_from_narration(narration)
    category = _infer_category(merchant, narration)

    return {
        "bank": "CanaraBank",
        "account_number": account_number,
        "transaction_type": transaction_type,
        "amount": amount,
        "date": date,
        "merchant": merchant or narration[:60] if narration else None,
        "upi_reference": upi_ref,
        "balance": balance,
        "category": category,
    }


def _extract_merchant_from_narration(narration: str) -> Optional[str]:
    """
    Try to extract merchant name from common Canara Bank narration patterns:
    - UPI-MERCHANT NAME-upi@bank-date-ref
    - NEFT/IMPS/NACH payee
    - POS/ATM transactions
    """
    if not narration:
        return None

    n = narration.strip()

    # UPI pattern: UPI/CR/ref/MerchantName/upi@vpa or UPI-MerchantName-vpa-ref
    m = re.search(
        r"UPI[/-](?:CR|DR|P2M|P2P)?[/-]?\d*[/-]([A-Za-z0-9 &._'-]{3,40})[/-]",
        n, re.IGNORECASE
    )
    if m:
        return m.group(1).strip()

    # NEFT/IMPS: NEFT CR-ref-SENDER NAME-... or IMPS/ref/MERCHANT
    m = re.search(
        r"(?:NEFT|IMPS|RTGS)[/ -](?:CR|DR)?[/ -]?\w*[/ -]([A-Za-z][A-Za-z0-9 &._'-]{2,40})",
        n, re.IGNORECASE
    )
    if m:
        return m.group(1).strip()

    # POS purchase: POS MERCHANT NAME DATE
    m = re.search(r"POS\s+([A-Za-z][A-Za-z0-9 &._'-]{3,40})\s+\d", n, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # ATW/ATM: just label as ATM Withdrawal
    if re.search(r"\b(?:ATW|ATM)\b", n, re.IGNORECASE):
        return "ATM Withdrawal"

    return None


def _extract_account_number(text: str) -> Optional[str]:
    """Try to find account number in statement header text."""
    m = re.search(r"(?:account\s*(?:no|number)[.:]?\s*)([0-9]{6,20})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"A/C\s*(?:No\.?)?\s*:?\s*([0-9]{6,20})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


# ── Text-based fallback parser ────────────────────────────────────────────────

# Pattern for statement lines where no proper table is detected
# Example: 01/07/26  UPI/CR/123456/MERCHANT/vpa  50.00  4,123.02
_TEXT_LINE_RE = re.compile(
    r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"       # date
    r"\s+(.{5,80}?)"                            # narration (non-greedy)
    r"\s+([\d,]+\.\d{2})"                       # debit or credit amount
    r"(?:\s+([\d,]+\.\d{2}))?"                  # optional second amount (balance or other side)
    r"(?:\s+([\d,]+\.\d{2}))?",                 # optional balance
    re.IGNORECASE
)


def _parse_text_lines(text: str, account_number: Optional[str]) -> List[Dict[str, Any]]:
    """Fallback: scan raw text lines for transaction patterns."""
    transactions = []
    for line in text.splitlines():
        m = _TEXT_LINE_RE.search(line)
        if not m:
            continue

        raw_date, narration, amt1, amt2, amt3 = m.groups()
        date = _parse_date(raw_date)
        if not date:
            continue

        amount = _clean_amount(amt1)
        if not amount or amount <= 0:
            continue

        # Infer debit/credit from narration keywords
        n_lower = narration.lower()
        if any(k in n_lower for k in ["cr ", "/cr/", "credit", "received", "salary", "refund", "cashback"]):
            transaction_type = "Credit"
        else:
            transaction_type = "Debit"

        balance = _clean_amount(amt3 or amt2)

        merchant = _extract_merchant_from_narration(narration)
        category = _infer_category(merchant, narration)

        upi_ref = None
        upi_m = re.search(r"(?:upi[/ -]?ref[: ]?|upi:?)(\d{8,})", narration, re.IGNORECASE)
        if upi_m:
            upi_ref = upi_m.group(1)

        transactions.append({
            "bank": "CanaraBank",
            "account_number": account_number,
            "transaction_type": transaction_type,
            "amount": amount,
            "date": date,
            "merchant": merchant or narration[:60].strip(),
            "upi_reference": upi_ref,
            "balance": balance,
            "category": category,
        })

    return transactions


# ── Public entry point ────────────────────────────────────────────────────────

def parse_bank_statement_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse a bank statement PDF and return a list of transaction dicts.

    Each dict has keys:
        bank, account_number, transaction_type, amount, date,
        merchant, upi_reference, balance, category

    Raises ValueError if no transactions could be extracted.
    """
    transactions: List[Dict[str, Any]] = []
    account_number: Optional[str] = None
    col_map: Dict[str, int] = {}
    header_found = False

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # Try to extract account number from first page text
            if account_number is None:
                page_text = page.extract_text() or ""
                account_number = _extract_account_number(page_text)

            # ── Table extraction (preferred) ─────────────────────────────
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                for row in table:
                    if row is None:
                        continue
                    cells = [c or "" for c in row]

                    # Detect header row
                    if not header_found:
                        candidate = _find_column_indices(cells)
                        if "date" in candidate and ("debit" in candidate or "credit" in candidate):
                            col_map = candidate
                            header_found = True
                            continue

                    if not header_found:
                        continue

                    txn = _parse_table_row(cells, col_map, account_number)
                    if txn:
                        transactions.append(txn)

            # ── Text fallback if no table transactions found on this page ──
            if not transactions:
                page_text = page.extract_text() or ""
                text_txns = _parse_text_lines(page_text, account_number)
                transactions.extend(text_txns)

    # Deduplicate by (date, amount, transaction_type, merchant)
    seen = set()
    unique: List[Dict[str, Any]] = []
    for t in transactions:
        key = (t["date"], t["amount"], t["transaction_type"], t.get("merchant"))
        if key not in seen:
            seen.add(key)
            unique.append(t)

    if not unique:
        raise ValueError(
            "No transactions found in the PDF. "
            "Make sure it is a Canara Bank statement with a transaction table."
        )

    return unique

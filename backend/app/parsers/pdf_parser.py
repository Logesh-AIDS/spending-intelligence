"""
PDF Bank Statement Parser — Canara Bank ePassbook (confirmed layout)

Each transaction block (from real PDF analysis):

    UPI/DR/658623275611/MR          ← particulars line 1
    ABISH/IDIB/**AN196@OKICICI/     ← particulars line 2
    UPI//AXI830FD7C66460404EA2      ← particulars line 3
    08-08-2026 91E06...14:49:05 27.50 514.22   ← DATE + middle + AMOUNT + BALANCE
    14:49:05                        ← timestamp (skip)
    Chq: 658623275611               ← UPI reference

Strategy:
  Pass 1 — find every line matching the date+amount pattern, record line index.
  Pass 2 — for each such line, collect particulars from lines since last Chq:.
"""

import re
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

import pdfplumber


# ── Regex patterns ────────────────────────────────────────────────────────────

# Date-amount line: DD-MM-YYYY [anything] amount [balance]
_TXN_RE = re.compile(
    r"^(\d{2}-\d{2}-\d{4})"       # date
    r"(.*?)"                        # middle (may be empty or partial hash)
    r"\s+([\d,]+\.\d{2})"          # amount
    r"(?:\s+([\d,]+\.\d{2}))?$"    # optional balance
)

_CHQ_RE     = re.compile(r"^Chq:\s*(\S*)$", re.IGNORECASE)
_HEADER_RE  = re.compile(r"Date\s+Particulars", re.IGNORECASE)
_TIME_RE    = re.compile(r"^\d{2}:\d{2}:\d{2}$")  # bare timestamp line

# Lines to discard entirely
_SKIP_WORDS = (
    "page ", "opening balance", "closing balance", "statement for",
    "customer id", "branch code", "name a logesh", "name ",
    "phone +", "phone+", "address", "ifsc code", "product code", "product name",
    "thottapatti", "namakkal", "mohanur", "branch name", "branch code",
    "disclaimer", "unless the",
    "beware of", "imb users", "change in the", "do not share",
    "ombudsman", "computer output", "end of statement",
    "bangalore", "e-mail:", "are you a merchant", "use digital",
    "contact branch", "xxxxxx",
)


def _skip(line: str) -> bool:
    lo = line.lower()
    return any(lo.startswith(w) for w in _SKIP_WORDS) or bool(_HEADER_RE.search(line))


def _parse_date(s: str) -> Optional[str]:
    try:
        return datetime.strptime(s.strip(), "%d-%m-%Y").strftime("%d/%m/%y")
    except ValueError:
        return None


def _to_float(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def _extract_merchant(particulars: str) -> Optional[str]:
    # UPI/DR or CR / ref / MERCHANT / ...
    m = re.match(r"UPI/(?:DR|CR)/\d+/([^/]+)", particulars, re.IGNORECASE)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    if re.match(r"APY\s+CONTRI", particulars, re.IGNORECASE):
        return "APY Contribution"
    m2 = re.match(r"(NEFT|IMPS|RTGS)", particulars, re.IGNORECASE)
    if m2:
        m3 = re.search(r"(?:NEFT|IMPS|RTGS)[/ -]\w+[/ -]([A-Za-z][A-Za-z0-9 ]+)", particulars, re.IGNORECASE)
        return m3.group(1).strip() if m3 else m2.group(1).upper() + " Transfer"
    return particulars[:50].strip() or None


def _infer_category(merchant: Optional[str], particulars: str) -> str:
    text = " ".join(filter(None, [merchant, particulars])).lower()
    rules = [
        (["zomato","swiggy","hotel","restaurant","cafe","food","biryani","pizza",
          "burger","dine","eat","kitchen","canteen","amman mess","amman tea",
          "sri cumin","vks resta","valli hot","madras ba","tea time","famous ca",
          "kings bak","sriva","srivaiga","mfc01","mfc 01"], "Food"),
        (["amazon","flipkart","myntra","ajio","nykaa","shop","mart","store",
          "purchase","meesho","reliance","bigbasket","blinkit","vsv trade",
          "v s v","vsv","delhivery"], "Shopping"),
        (["uber","ola","rapido","irctc","railway","air","flight","bus","metro",
          "toll","petrol","fuel","cab","nps petro","airp","sillobi"], "Travel"),
        (["electricity","water","gas","broadband","internet","mobile","recharge",
          "jio","vi ","bsnl","bill","insurance","lic ","postpaid","sbipmopad",
          "google pl","apy contri","sbibhim","sbipmop","airtel"], "Bills"),
        (["hospital","pharmacy","medical","clinic","doctor","apollo","health",
          "medicine","lab","diagnostic"], "Health"),
        (["netflix","prime","hotstar","spotify","youtube","game","cinema","movie",
          "entertainment","pvr","inox"], "Entertainment"),
        (["school","college","university","tuition","course","udemy","coursera",
          "education","fee","exam"], "Education"),
        (["salary","payroll","wages","stipend","sks poly","skspoly"], "Salary"),
    ]
    for keywords, cat in rules:
        if any(kw in text for kw in keywords):
            return cat
    return "Others"


def _parse_page(text: str, account_number: Optional[str]) -> List[Dict[str, Any]]:
    lines = [l.rstrip() for l in text.splitlines()]
    results: List[Dict[str, Any]] = []

    # Rolling buffer of non-skip, non-timestamp lines since last Chq:
    # These become the particulars for the NEXT transaction line.
    partic_buffer: List[str] = []

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1

        if not line:
            continue

        # Discard known header/footer/info lines
        if _skip(line):
            continue

        # Timestamp-only line (e.g. "14:49:05") — skip
        if _TIME_RE.match(line):
            continue

        # Chq line — extract ref, then reset buffer for next transaction
        chq_m = _CHQ_RE.match(line)
        if chq_m:
            # ref was already attached to the last transaction; just clear buffer
            partic_buffer = []
            continue

        # Transaction line?
        txn_m = _TXN_RE.match(line)
        if txn_m:
            date    = _parse_date(txn_m.group(1))
            middle  = txn_m.group(2).strip()
            amount  = _to_float(txn_m.group(3))
            balance = _to_float(txn_m.group(4)) if txn_m.group(4) else None

            if not date or not amount or amount <= 0:
                partic_buffer.append(line)
                continue

            # Particulars = buffer accumulated since last Chq:
            # Append middle segment (partial hash/text on the txn line itself)
            all_parts = partic_buffer[:]
            if middle:
                all_parts.append(middle)
            particulars = " ".join(all_parts)

            # Look ahead for Chq line to get UPI ref
            upi_ref: Optional[str] = None
            for j in range(i, min(i + 3, len(lines))):
                ahead = lines[j].strip()
                cm = _CHQ_RE.match(ahead)
                if cm:
                    upi_ref = cm.group(1) if cm.group(1) else None
                    break

            # If no Chq ref, extract from particulars
            if not upi_ref:
                m2 = re.match(r"UPI/(?:DR|CR)/(\d+)/", particulars, re.IGNORECASE)
                if m2:
                    upi_ref = m2.group(1)

            # Credit vs Debit
            if re.search(r"UPI/CR/", particulars, re.IGNORECASE):
                txn_type = "Credit"
            elif re.search(r"UPI/DR/", particulars, re.IGNORECASE):
                txn_type = "Debit"
            else:
                txn_type = "Credit" if re.search(
                    r"\b(credit|received|salary|refund|cashback)\b",
                    particulars, re.IGNORECASE
                ) else "Debit"

            merchant  = _extract_merchant(particulars)
            category  = _infer_category(merchant, particulars)

            results.append({
                "bank": "CanaraBank",
                "account_number": account_number,
                "transaction_type": txn_type,
                "amount": amount,
                "date": date,
                "merchant": merchant,
                "upi_reference": upi_ref,
                "balance": balance,
                "category": category,
            })

            # Clear buffer — Chq line (seen in look-ahead) will clear it officially
            partic_buffer = []
            continue

        # Otherwise: accumulate into particulars buffer
        partic_buffer.append(line)

    return results


def _extract_account_number(text: str) -> Optional[str]:
    m = re.search(r"A/c\s+([X0-9]+)", text)
    return m.group(1) if m else None


def parse_bank_statement_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse a Canara Bank ePassbook PDF.
    Returns list of transaction dicts.
    Raises ValueError if nothing could be parsed.
    """
    all_txns: List[Dict[str, Any]] = []
    account_number: Optional[str] = None

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""
            if account_number is None:
                account_number = _extract_account_number(text)
            all_txns.extend(_parse_page(text, account_number))

    # Deduplicate by UPI ref first, then date+amount+type
    seen_refs: set = set()
    seen_keys: set = set()
    unique: List[Dict[str, Any]] = []

    for t in all_txns:
        ref = t.get("upi_reference")
        key = (t["date"], t["amount"], t["transaction_type"])
        if ref and ref in seen_refs:
            continue
        if not ref and key in seen_keys:
            continue
        if ref:
            seen_refs.add(ref)
        seen_keys.add(key)
        unique.append(t)

    if not unique:
        raise ValueError(
            "No transactions found in the PDF. "
            "Please upload a Canara Bank ePassbook statement."
        )

    return unique

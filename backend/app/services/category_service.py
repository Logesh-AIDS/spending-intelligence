"""
AI-powered category assignment.
Uses merchant name + keywords to assign the most accurate category.
No ML model needed — rule-based AI with comprehensive merchant knowledge.
"""

# Merchant keyword → category mapping
# More specific patterns first, then general ones
MERCHANT_CATEGORY_RULES = [
    # Food & Dining
    ("food", ["zomato", "swiggy", "dunzo", "bigbasket", "grofers", "blinkit",
              "dominos", "pizza", "kfc", "mcdonalds", "subway", "hotel",
              "restaurant", "biryani", "mess", "canteen", "cafe", "coffee",
              "dhaba", "snacks", "bakery", "meals", "lunch", "dinner",
              "cumin", "amman", "keerthi", "kalidass", "kumar hotel",
              "vibin", "seeds", "fruits", "vegetables", "grocery"]),

    # Shopping & E-commerce
    ("shopping", ["flipkart", "amazon", "myntra", "ajio", "meesho", "snapdeal",
                  "nykaa", "tata cliq", "reliance", "dmart", "bigbazar",
                  "shoppers stop", "lifestyle", "max fashion", "h&m",
                  "shopping", "mall", "store", "mart", "market"]),

    # Travel & Transport
    ("travel", ["ola", "uber", "rapido", "redbus", "irctc", "makemytrip",
                "yatra", "goibibo", "cleartrip", "airline", "airways",
                "railway", "metro", "bus", "auto", "cab", "taxi",
                "fuel", "petrol", "diesel", "parking", "toll",
                "transport", "travel", "vsv tra"]),

    # Utilities & Bills
    ("bills", ["electricity", "water", "gas", "internet", "broadband",
               "airtel", "jio", "vodafone", "bsnl", "act ", "hathway",
               "tata sky", "dish tv", "sun direct", "recharge",
               "tneb", "bescom", "mseb", "bill", "utility",
               "phonepay", "paytm", "gpay", "upi payment"]),

    # Healthcare
    ("health", ["apollo", "fortis", "hospital", "clinic", "pharmacy",
                "medplus", "netmeds", "1mg", "practo", "doctor",
                "medical", "medicine", "health", "dental", "optical",
                "lab", "diagnostic", "pathology", "nursing"]),

    # Entertainment
    ("entertainment", ["netflix", "amazon prime", "hotstar", "zee5", "sony liv",
                       "pvr", "inox", "carnival", "movie", "cinema", "theatre",
                       "spotify", "apple music", "youtube", "gaming",
                       " pub ", "entertainment"]),

    # Education
    ("education", ["school", "college", "university", "course", "tuition",
                   "coaching", "udemy", "coursera", "byju", "unacademy",
                   "education", "fee", "exam", "books", "stationery"]),

    # Salary & Income
    ("salary", ["salary", "stipend", "payroll", "employer", "company",
                "wages", "income", "payment received", "credited by"]),

    # Investment & Savings
    ("investment", ["mutual fund", "sip", "groww", "zerodha", "upstox",
                    "angel", "hdfc securities", "icici securities",
                    "insurance", "lic", "premium", "fd", "fixed deposit",
                    "rd", "recurring", "investment", "savings"]),

    # Personal transfers
    ("transfer", ["neft", "imps", "rtgs", "fund transfer",
                  "mr ", "mrs ", "ms ", "sri ", "shri ",
                  "mahendran", "subha", "vishnu", "rajakumari",
                  "srivishnuvar", "dhivyadharsi", "barkath"]),
]

# Category display names and colors
CATEGORY_META = {
    "food":        {"label": "Food & Dining",    "emoji": "🍽️",  "color": "#FF6B35"},
    "shopping":    {"label": "Shopping",          "emoji": "🛍️",  "color": "#7C3AED"},
    "travel":      {"label": "Travel",            "emoji": "🚗",  "color": "#00A3FF"},
    "bills":       {"label": "Bills & Utilities", "emoji": "⚡",  "color": "#FF4D6A"},
    "health":      {"label": "Health",            "emoji": "🏥",  "color": "#00C896"},
    "entertainment": {"label": "Entertainment",  "emoji": "🎬",  "color": "#FFBF00"},
    "education":   {"label": "Education",         "emoji": "📚",  "color": "#1A56DB"},
    "salary":      {"label": "Salary",            "emoji": "💰",  "color": "#00C896"},
    "investment":  {"label": "Investment",        "emoji": "📈",  "color": "#10B981"},
    "transfer":    {"label": "Transfer",          "emoji": "↔️",  "color": "#6B7DB3"},
    "others":      {"label": "Others",            "emoji": "💳",  "color": "#9CA3AF"},
}


def categorize(merchant: str, transaction_type: str = "Debit") -> str:
    """
    Assign a category based on merchant name and transaction type.

    Args:
        merchant: merchant/receiver name from SMS
        transaction_type: "Debit" or "Credit"

    Returns:
        category string
    """
    if not merchant:
        return "others"

    merchant_lower = merchant.lower().strip()

    # Credits with high amounts are likely salary
    if transaction_type == "Credit":
        if any(k in merchant_lower for k in ["salary", "payroll", "employer", "company"]):
            return "salary"
        # Person-to-person credit transfers
        return "transfer"

    # Check rules in order
    for category, keywords in MERCHANT_CATEGORY_RULES:
        if any(keyword in merchant_lower for keyword in keywords):
            return category

    return "others"


def get_category_label(category: str) -> str:
    """Get the display-friendly label for a category."""
    return CATEGORY_META.get(category, {}).get("label", category.title())


def get_category_emoji(category: str) -> str:
    """Get the emoji for a category."""
    return CATEGORY_META.get(category, {}).get("emoji", "💳")

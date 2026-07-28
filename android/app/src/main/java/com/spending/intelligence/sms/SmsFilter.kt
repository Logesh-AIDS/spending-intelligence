package com.spending.intelligence.sms

/**
 * Filters incoming SMS to determine if it's a supported bank transaction SMS.
 * Returns null for OTPs, promotional messages, and unsupported banks.
 */
object SmsFilter {

    // Supported bank sender IDs
    private val SUPPORTED_SENDERS = setOf(
        "CANBNK", "CANARABANK", "CANARA",
        "HDFCBK", "HDFC",
        "SBIINB", "SBIUPI", "SBI",
        "ICICIB", "ICICI",
        "AXISBK", "AXIS",
        "KOTAKB", "KOTAK",
        "PNBSMS", "PNB",
        "BOIIND", "BANKOFIND"
    )

    // Keywords that indicate a transaction (not OTP or promo)
    private val TRANSACTION_KEYWORDS = listOf(
        "debited", "credited", "debit", "credit",
        "Dr.", "Cr.", "INR", "Rs.", "₹",
        "transaction", "transfer", "payment",
        "withdrawn", "deposited", "balance"
    )

    // Keywords that indicate OTP — always skip these
    private val OTP_KEYWORDS = listOf(
        "OTP", "One Time Password", "verification code",
        "not share", "do not share", "confidential"
    )

    // Keywords that indicate promotional messages — skip
    private val PROMO_KEYWORDS = listOf(
        "offer", "discount", "cashback", "reward",
        "earn points", "click here", "limited time",
        "congratulations", "winner", "prize"
    )

    /**
     * Returns the raw SMS body if it should be forwarded to the backend.
     * Returns null if the SMS should be ignored.
     */
    fun filter(sender: String, body: String): String? {
        val senderUpper = sender.uppercase()
        val bodyUpper = body.uppercase()

        // Must be from a supported bank sender
        val isSupportedBank = SUPPORTED_SENDERS.any { senderUpper.contains(it) } ||
                TRANSACTION_KEYWORDS.any { body.contains(it, ignoreCase = true) } &&
                (body.contains("INR", ignoreCase = false) || body.contains("Rs.") || body.contains("₹"))

        if (!isSupportedBank) return null

        // Reject OTPs
        if (OTP_KEYWORDS.any { body.contains(it, ignoreCase = true) }) return null

        // Reject promotions
        if (PROMO_KEYWORDS.any { body.contains(it, ignoreCase = true) }) return null

        // Must contain a monetary amount pattern
        val hasAmount = Regex("""(?:INR|Rs\.?|₹)\s*[\d,]+\.?\d*""").containsMatchIn(body)
        if (!hasAmount) return null

        return body
    }

    fun isBankSender(sender: String): Boolean =
        SUPPORTED_SENDERS.any { sender.uppercase().contains(it) }
}

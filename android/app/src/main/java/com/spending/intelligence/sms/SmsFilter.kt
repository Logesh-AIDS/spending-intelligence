package com.spending.intelligence.sms

import android.util.Log

object SmsFilter {
    private const val TAG = "SmsFilter"

    // All real sender IDs observed from Canara Bank
    private val BANK_SENDERS = listOf(
        "canara", "canarabank", "canbnk", "canbank",
        "ax-canbnk", "ad-canbnk", "vk-canbnk", "tm-canbnk",
        "hdfcbk", "hdfc", "sbiupi", "sbiinb", "sbi",
        "icicib", "icici", "axisbk", "axis",
        "kotak", "pnb", "iob", "boi"
    )

    // OTP indicators — always skip
    private val OTP_KEYWORDS = listOf(
        "one time password", "otp for", "otp is", "your otp",
        "verification code", "do not share", "not share your otp"
    )

    fun filter(sender: String, body: String): String? {
        val senderLower = sender.lowercase()
        val bodyLower = body.lowercase()

        Log.d(TAG, "SMS from='$sender' body=${body.take(60)}")

        // Skip OTPs immediately
        if (OTP_KEYWORDS.any { bodyLower.contains(it) }) {
            Log.d(TAG, "SKIPPED: OTP")
            return null
        }

        // Check if it's from a bank sender
        val isBankSender = BANK_SENDERS.any { senderLower.contains(it) }

        // Check if body looks like a transaction
        val hasAmount = Regex("""(?:inr|rs\.?|₹)\s*[\d,]+""", RegexOption.IGNORE_CASE).containsMatchIn(body)
        val hasDebitCredit = bodyLower.contains("dr.") || bodyLower.contains("cr.") ||
                bodyLower.contains("debited") || bodyLower.contains("credited") ||
                bodyLower.contains("paid thru") || bodyLower.contains("has been debit")

        if (isBankSender && hasAmount && (hasDebitCredit || bodyLower.contains("bal "))) {
            Log.d(TAG, "ACCEPTED")
            return body
        }

        Log.d(TAG, "SKIPPED: not a transaction")
        return null
    }
}

package com.spending.intelligence.sms

import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.Calendar
import javax.inject.Inject
import javax.inject.Singleton

data class SmsMessage(
    val id: String,              // Android SMS database ID — truly unique per message
    val sender: String,
    val body: String,
    val timestamp: Long          // milliseconds since epoch
)

@Singleton
class SmsReader @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val TAG = "SmsReader"

    /**
     * Read bank SMS from the current month only.
     * Returns only messages that pass the bank SMS filter.
     */
    fun readCurrentMonthBankSms(): List<SmsMessage> {
        // Start of current month at midnight
        val cal = Calendar.getInstance().apply {
            set(Calendar.DAY_OF_MONTH, 1)
            set(Calendar.HOUR_OF_DAY, 0)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        val monthStartMs = cal.timeInMillis

        return readBankSmsFrom(monthStartMs)
    }

    /**
     * Read bank SMS from a specific timestamp onwards.
     */
    fun readBankSmsFrom(fromTimestampMs: Long): List<SmsMessage> {
        val results = mutableListOf<SmsMessage>()

        try {
            val uri = Uri.parse("content://sms/inbox")
            val cursor: Cursor? = context.contentResolver.query(
                uri,
                arrayOf("_id", "address", "body", "date"),
                "date >= ?",
                arrayOf(fromTimestampMs.toString()),
                "date DESC"   // newest first
            )

            cursor?.use { c ->
                Log.d(TAG, "SMS in inbox from cutoff: ${c.count}")
                while (c.moveToNext()) {
                    val id = c.getString(c.getColumnIndexOrThrow("_id")) ?: continue
                    val sender = c.getString(c.getColumnIndexOrThrow("address")) ?: continue
                    val body = c.getString(c.getColumnIndexOrThrow("body")) ?: continue
                    val timestamp = c.getLong(c.getColumnIndexOrThrow("date"))

                    val filtered = SmsFilter.filter(sender, body)
                    if (filtered != null) {
                        results.add(SmsMessage(id, sender, filtered, timestamp))
                    }
                }
            }

            Log.d(TAG, "Found ${results.size} bank SMS this month")
        } catch (e: Exception) {
            Log.e(TAG, "Error reading SMS inbox: ${e.message}", e)
        }

        return results
    }
}

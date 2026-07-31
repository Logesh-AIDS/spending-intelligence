package com.spending.intelligence.sms

import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

data class SmsMessage(
    val id: String,
    val sender: String,
    val body: String,
    val timestamp: Long
)

/**
 * Reads SMS directly from the device inbox.
 * More reliable than broadcast receiver on restricted devices (Xiaomi, Samsung, etc.)
 */
@Singleton
class SmsReader @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val TAG = "SmsReader"

    /**
     * Read all bank SMS from inbox, from last N days.
     * Returns list of (sender, body) pairs that pass the filter.
     */
    fun readBankSms(daysBack: Int = 90): List<SmsMessage> {
        val results = mutableListOf<SmsMessage>()

        try {
            val uri = Uri.parse("content://sms/inbox")
            val cutoffMs = System.currentTimeMillis() - (daysBack.toLong() * 24 * 60 * 60 * 1000)

            val cursor: Cursor? = context.contentResolver.query(
                uri,
                arrayOf("_id", "address", "body", "date"),
                "date > ?",
                arrayOf(cutoffMs.toString()),
                "date DESC"
            )

            cursor?.use { c ->
                Log.d(TAG, "Total SMS in inbox: ${c.count}")
                while (c.moveToNext()) {
                    val id = c.getString(c.getColumnIndexOrThrow("_id")) ?: continue
                    val sender = c.getString(c.getColumnIndexOrThrow("address")) ?: continue
                    val body = c.getString(c.getColumnIndexOrThrow("body")) ?: continue
                    val date = c.getLong(c.getColumnIndexOrThrow("date"))

                    val filtered = SmsFilter.filter(sender, body)
                    if (filtered != null) {
                        results.add(SmsMessage(id, sender, filtered, date))
                        Log.d(TAG, "Found bank SMS from $sender: ${body.take(50)}")
                    }
                }
            }

            Log.d(TAG, "Found ${results.size} bank SMS messages")
        } catch (e: Exception) {
            Log.e(TAG, "Error reading SMS inbox: ${e.message}", e)
        }

        return results
    }
}

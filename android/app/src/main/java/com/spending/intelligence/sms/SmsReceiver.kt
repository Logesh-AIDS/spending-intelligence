package com.spending.intelligence.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.local.entity.PendingSmsEntity
import com.spending.intelligence.data.remote.api.SpendingApi
import com.spending.intelligence.data.remote.dto.SmsRequest
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Receives incoming SMS instantly.
 * Calls the backend API directly in a coroutine — no WorkManager delay.
 * Falls back to local queue if network is unavailable.
 */
@AndroidEntryPoint
class SmsReceiver : BroadcastReceiver() {

    @Inject lateinit var pendingSmsDao: PendingSmsDao
    @Inject lateinit var api: SpendingApi

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        val pendingResult = goAsync() // keeps receiver alive during async work

        CoroutineScope(Dispatchers.IO).launch {
            try {
                for (msg in messages) {
                    val sender = msg.originatingAddress ?: continue
                    val body = msg.messageBody ?: continue

                    val filteredSms = SmsFilter.filter(sender, body) ?: continue

                    Log.d("SmsReceiver", "Bank SMS detected: ${body.take(50)}")

                    // Try direct API call first (instant if online)
                    try {
                        val response = api.parseSms(SmsRequest(filteredSms))
                        if (response.isSuccessful) {
                            Log.d("SmsReceiver", "✅ SMS uploaded instantly")
                        } else if (response.code() == 422) {
                            Log.w("SmsReceiver", "SMS format not supported (422)")
                        } else {
                            // API failed — save to queue for retry
                            pendingSmsDao.insert(PendingSmsEntity(rawSms = filteredSms))
                            Log.w("SmsReceiver", "API returned ${response.code()} — queued for retry")
                        }
                    } catch (networkError: Exception) {
                        // No internet — save to queue, WorkManager will retry
                        pendingSmsDao.insert(PendingSmsEntity(rawSms = filteredSms))
                        Log.w("SmsReceiver", "Offline — SMS queued: ${networkError.message}")
                    }
                }
            } finally {
                pendingResult.finish()
            }
        }
    }
}

package com.spending.intelligence.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import com.spending.intelligence.data.local.TokenHolder
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.local.entity.PendingSmsEntity
import com.spending.intelligence.data.remote.api.SpendingApi
import com.spending.intelligence.data.remote.dto.SmsRequest
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "SmsReceiver"

@AndroidEntryPoint
class SmsReceiver : BroadcastReceiver() {

    @Inject lateinit var pendingSmsDao: PendingSmsDao
    @Inject lateinit var api: SpendingApi
    @Inject lateinit var tokenHolder: TokenHolder

    override fun onReceive(context: Context, intent: Intent) {
        Log.d(TAG, "onReceive called with action: ${intent.action}")

        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            Log.d(TAG, "Ignoring non-SMS action")
            return
        }

        val messages = try {
            Telephony.Sms.Intents.getMessagesFromIntent(intent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get messages: ${e.message}")
            return
        }

        if (messages.isNullOrEmpty()) {
            Log.w(TAG, "No messages in intent")
            return
        }

        val pendingResult = goAsync()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                for (msg in messages) {
                    val sender = msg.originatingAddress ?: "Unknown"
                    val body = msg.messageBody ?: continue

                    Log.d(TAG, "SMS from '$sender': ${body.take(80)}")

                    val filteredBody = SmsFilter.filter(sender, body)
                    if (filteredBody == null) {
                        Log.d(TAG, "SMS filtered out")
                        continue
                    }

                    Log.d(TAG, "Processing bank SMS from $sender")

                    // Always save to local queue first (offline safety)
                    val queueId = pendingSmsDao.insert(PendingSmsEntity(rawSms = filteredBody))
                    Log.d(TAG, "Saved to queue with id=$queueId")

                    // Try immediate upload if token is available
                    val token = tokenHolder.token
                    if (!token.isNullOrBlank()) {
                        try {
                            Log.d(TAG, "Uploading SMS to backend immediately...")
                            val response = api.parseSms(SmsRequest(filteredBody))
                            when {
                                response.isSuccessful -> {
                                    pendingSmsDao.deleteById(queueId)
                                    Log.d(TAG, "✅ SMS uploaded instantly, removed from queue")
                                }
                                response.code() == 422 -> {
                                    pendingSmsDao.deleteById(queueId)
                                    Log.w(TAG, "SMS format not supported (422) — removed from queue")
                                }
                                else -> {
                                    Log.w(TAG, "Upload failed (${response.code()}) — will retry from queue")
                                }
                            }
                        } catch (networkError: Exception) {
                            Log.w(TAG, "Network error — SMS stays in queue: ${networkError.message}")
                        }
                    } else {
                        Log.w(TAG, "No token available — SMS queued for later upload")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Unexpected error in SMS processing: ${e.message}", e)
            } finally {
                pendingResult.finish()
            }
        }
    }
}

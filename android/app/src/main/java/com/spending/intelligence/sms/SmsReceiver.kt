package com.spending.intelligence.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.spending.intelligence.worker.SmsSyncWorker
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.local.entity.PendingSmsEntity

/**
 * Receives incoming SMS broadcast.
 * Filters for bank transaction messages.
 * Queues them to Room (offline-safe) then triggers WorkManager upload.
 */
@AndroidEntryPoint
class SmsReceiver : BroadcastReceiver() {

    @Inject
    lateinit var pendingSmsDao: PendingSmsDao

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        val scope = CoroutineScope(Dispatchers.IO)

        for (msg in messages) {
            val sender = msg.originatingAddress ?: continue
            val body = msg.messageBody ?: continue

            val filteredSms = SmsFilter.filter(sender, body) ?: continue

            Log.d("SmsReceiver", "Bank SMS detected from $sender")

            scope.launch {
                // 1. Save to local queue (works offline)
                val pendingId = pendingSmsDao.insert(PendingSmsEntity(rawSms = filteredSms))
                Log.d("SmsReceiver", "Queued SMS id=$pendingId")

                // 2. Trigger WorkManager to upload immediately (if online)
                val uploadWork = OneTimeWorkRequestBuilder<SmsSyncWorker>()
                    .build()
                WorkManager.getInstance(context).enqueue(uploadWork)
            }
        }
    }
}

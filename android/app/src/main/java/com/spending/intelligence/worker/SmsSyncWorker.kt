package com.spending.intelligence.worker

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.ServiceInfo
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.spending.intelligence.data.local.TokenHolder
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.remote.api.SpendingApi
import com.spending.intelligence.data.remote.dto.SmsRequest
import com.spending.intelligence.sms.SmsReader
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit

private const val TAG = "SmsSyncWorker"
private const val PREFS_NAME = "sms_uploaded_ids"

@HiltWorker
class SmsSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val api: SpendingApi,
    private val pendingSmsDao: PendingSmsDao,
    private val tokenHolder: TokenHolder,
    private val smsReader: SmsReader,
) : CoroutineWorker(context, workerParams) {

    companion object {
        const val TAG_PERIODIC = "SmsSyncWorker"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "sms_sync"

        fun buildPeriodicRequest(): PeriodicWorkRequest =
            PeriodicWorkRequestBuilder<SmsSyncWorker>(15, TimeUnit.MINUTES)
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .addTag(TAG_PERIODIC)
                .build()
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        val nm = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            nm.createNotificationChannel(NotificationChannel(CHANNEL_ID, "SMS Sync", NotificationManager.IMPORTANCE_LOW))
        }
        val notification: Notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("SpendControl")
            .setContentText("Scanning bank messages...")
            .setSmallIcon(android.R.drawable.ic_popup_sync)
            .setOngoing(true)
            .build()
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q)
            ForegroundInfo(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        else ForegroundInfo(NOTIFICATION_ID, notification)
    }

    override suspend fun doWork(): Result {
        val token = tokenHolder.token
        if (token.isNullOrBlank()) {
            Log.w(TAG, "No token — skipping sync")
            return Result.success()
        }

        // SharedPrefs stores SMS IDs that have already been uploaded — prevents duplicates
        val prefs = applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val uploadedIds = prefs.getStringSet("uploaded_sms_ids", mutableSetOf())!!.toMutableSet()

        var uploadedCount = 0

        // Step 1: Upload queued SMS (from broadcast receiver)
        pendingSmsDao.deleteExhausted()
        val pending = pendingSmsDao.getPending()
        for (sms in pending) {
            try {
                val response = api.parseSms(SmsRequest(sms.rawSms))
                when {
                    response.isSuccessful || response.code() == 422 -> {
                        pendingSmsDao.deleteById(sms.id)
                        if (response.isSuccessful) uploadedCount++
                    }
                    else -> pendingSmsDao.incrementRetry(sms.id)
                }
            } catch (e: Exception) {
                pendingSmsDao.incrementRetry(sms.id)
            }
        }

        // Step 2: Scan inbox for ALL bank messages not yet uploaded
        try {
            val bankMessages = smsReader.readBankSms(daysBack = 90) // scan 90 days back
            Log.d(TAG, "Found ${bankMessages.size} bank messages, ${uploadedIds.size} already uploaded")

            val newMessages = bankMessages.filter { !uploadedIds.contains(it.id) }
            Log.d(TAG, "New messages to upload: ${newMessages.size}")

            for (msg in newMessages) {
                try {
                    val response = api.parseSms(SmsRequest(msg.body))
                    if (response.isSuccessful) {
                        // Mark as uploaded so it's never sent again
                        uploadedIds.add(msg.id)
                        uploadedCount++
                        Log.d(TAG, "✅ Uploaded SMS id=${msg.id}")
                    } else if (response.code() == 422) {
                        // Unsupported format — mark as seen so we don't retry endlessly
                        uploadedIds.add(msg.id)
                        Log.d(TAG, "Skipped unsupported SMS id=${msg.id}")
                    }
                    // Network errors: don't add to uploadedIds — will retry next sync
                } catch (e: Exception) {
                    Log.w(TAG, "Upload failed for SMS id=${msg.id}: ${e.message}")
                }
            }

            // Persist updated set (keep only last 1000 to avoid unbounded growth)
            val trimmed = if (uploadedIds.size > 1000) uploadedIds.takeLast(1000).toSet() else uploadedIds
            prefs.edit().putStringSet("uploaded_sms_ids", trimmed).apply()

        } catch (e: Exception) {
            Log.e(TAG, "Inbox scan failed: ${e.message}")
        }

        Log.d(TAG, "Sync done: $uploadedCount new transactions")
        return Result.success()
    }
}

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

// SharedPreferences key — stores set of Android SMS IDs already uploaded
private const val PREFS_UPLOADED = "sms_uploaded_ids"
private const val KEY_IDS = "uploaded_sms_ids"

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
                .setConstraints(
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
            nm.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "SMS Sync", NotificationManager.IMPORTANCE_LOW)
            )
        }
        val notification: Notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("SpendControl")
            .setContentText("Syncing transactions...")
            .setSmallIcon(android.R.drawable.ic_popup_sync)
            .setOngoing(true)
            .build()

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q)
            ForegroundInfo(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        else
            ForegroundInfo(NOTIFICATION_ID, notification)
    }

    override suspend fun doWork(): Result {
        val token = tokenHolder.token
        if (token.isNullOrBlank()) {
            Log.w(TAG, "No token — skipping sync")
            return Result.success()
        }

        val prefs = applicationContext.getSharedPreferences(PREFS_UPLOADED, Context.MODE_PRIVATE)

        // Thread-safe read of uploaded IDs
        val uploadedIds = prefs.getStringSet(KEY_IDS, emptySet())!!.toMutableSet()
        var newUploaded = 0

        // ── Step 1: Flush any queued SMS from broadcast receiver ──────────────
        pendingSmsDao.deleteExhausted()
        for (sms in pendingSmsDao.getPending()) {
            try {
                val r = api.parseSms(SmsRequest(sms.rawSms))
                when {
                    r.isSuccessful || r.code() == 422 -> {
                        pendingSmsDao.deleteById(sms.id)
                        if (r.isSuccessful) newUploaded++
                    }
                    else -> pendingSmsDao.incrementRetry(sms.id)
                }
            } catch (e: Exception) {
                pendingSmsDao.incrementRetry(sms.id)
            }
        }

        // ── Step 2: Scan current month's inbox ────────────────────────────────
        try {
            val bankMessages = smsReader.readCurrentMonthBankSms()
            Log.d(TAG, "Current month: ${bankMessages.size} bank SMS, ${uploadedIds.size} already uploaded")

            val toUpload = bankMessages.filter { !uploadedIds.contains(it.id) }
            Log.d(TAG, "New to upload: ${toUpload.size}")

            for (msg in toUpload) {
                try {
                    val r = api.parseSms(SmsRequest(msg.body))
                    when {
                        r.isSuccessful -> {
                            uploadedIds.add(msg.id)
                            newUploaded++
                            Log.d(TAG, "✅ Uploaded sms id=${msg.id}")
                        }
                        r.code() == 422 -> {
                            // Unsupported format — mark seen so we don't retry
                            uploadedIds.add(msg.id)
                            Log.d(TAG, "Format not supported id=${msg.id}")
                        }
                        // Network/server error — don't mark as uploaded, retry next time
                        else -> Log.w(TAG, "Upload failed (${r.code()}) for id=${msg.id}")
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "Network error for id=${msg.id}: ${e.message}")
                    // Don't mark as uploaded — will retry
                }
            }

            // Persist uploaded IDs (keep max 2000 to avoid unbounded growth)
            val toSave = if (uploadedIds.size > 2000) {
                uploadedIds.toList().takeLast(2000).toSet()
            } else uploadedIds

            prefs.edit().putStringSet(KEY_IDS, toSave).apply()

        } catch (e: Exception) {
            Log.e(TAG, "Inbox scan error: ${e.message}")
        }

        Log.d(TAG, "Sync complete: $newUploaded new transactions")
        return Result.success()
    }
}

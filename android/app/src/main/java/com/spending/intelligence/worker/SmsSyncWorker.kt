package com.spending.intelligence.worker

import android.content.Context
import android.util.Log
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.remote.api.SpendingApi
import com.spending.intelligence.data.remote.dto.SmsRequest
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit

/**
 * Uploads pending SMS to backend.
 * Runs when network is available.
 * Retries on failure with exponential backoff.
 * Removes successfully uploaded SMS from the local queue.
 */
@HiltWorker
class SmsSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val api: SpendingApi,
    private val pendingSmsDao: PendingSmsDao,
) : CoroutineWorker(context, workerParams) {

    companion object {
        const val TAG = "SmsSyncWorker"

        fun buildPeriodicRequest(): PeriodicWorkRequest =
            PeriodicWorkRequestBuilder<SmsSyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .addTag(TAG)
                .build()
    }

    override suspend fun doWork(): Result {
        // Remove exhausted entries first (retried 5+ times)
        pendingSmsDao.deleteExhausted()

        val pending = pendingSmsDao.getPending()
        if (pending.isEmpty()) return Result.success()

        Log.d(TAG, "Uploading ${pending.size} pending SMS messages")

        var anyFailed = false

        for (sms in pending) {
            try {
                val response = api.parseSms(SmsRequest(sms.rawSms))
                if (response.isSuccessful) {
                    pendingSmsDao.deleteById(sms.id)
                    Log.d(TAG, "SMS id=${sms.id} uploaded successfully")
                } else if (response.code() == 422) {
                    // Unprocessable — the SMS format isn't supported, don't retry
                    pendingSmsDao.deleteById(sms.id)
                    Log.w(TAG, "SMS id=${sms.id} rejected by backend (422), removed from queue")
                } else {
                    pendingSmsDao.incrementRetry(sms.id)
                    anyFailed = true
                    Log.w(TAG, "SMS id=${sms.id} failed with ${response.code()}, will retry")
                }
            } catch (e: Exception) {
                pendingSmsDao.incrementRetry(sms.id)
                anyFailed = true
                Log.e(TAG, "Network error for SMS id=${sms.id}: ${e.message}")
            }
        }

        return if (anyFailed) Result.retry() else Result.success()
    }
}

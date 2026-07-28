package com.spending.intelligence

import android.app.Application
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.*
import com.spending.intelligence.worker.SmsSyncWorker
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class SpendingApp : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()

    override fun onCreate() {
        super.onCreate()
        schedulePeriodicSync()
    }

    private fun schedulePeriodicSync() {
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            SmsSyncWorker.TAG,
            ExistingPeriodicWorkPolicy.KEEP,
            SmsSyncWorker.buildPeriodicRequest()
        )
    }
}

package com.spending.intelligence.presentation

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.navigation.compose.rememberNavController
import androidx.work.*
import com.spending.intelligence.data.local.TokenDataStore
import com.spending.intelligence.data.local.TokenHolder
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.navigation.SpendingNavGraph
import com.spending.intelligence.presentation.theme.SpendingTheme
import com.spending.intelligence.worker.SmsSyncWorker
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject lateinit var tokenDataStore: TokenDataStore
    @Inject lateinit var tokenHolder: TokenHolder

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        val smsGranted = results[Manifest.permission.READ_SMS] == true
        if (smsGranted) {
            // SMS permission just granted — trigger sync immediately
            triggerImmediateSync()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore token BEFORE UI renders
        val savedToken = runBlocking { tokenDataStore.token.first() }
        if (!savedToken.isNullOrBlank()) {
            tokenHolder.token = savedToken
        }

        val startDestination = if (!savedToken.isNullOrBlank()) Screen.Dashboard.route
        else Screen.Login.route

        // Request all required permissions
        val permissions = mutableListOf(
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.READ_SMS
        )
        // POST_NOTIFICATIONS needed on Android 13+
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        permissionLauncher.launch(permissions.toTypedArray())

        // If already logged in, trigger inbox scan immediately
        if (!savedToken.isNullOrBlank()) {
            triggerImmediateSync()
        }

        setContent {
            SpendingTheme {
                val navController = rememberNavController()
                SpendingNavGraph(navController = navController, startDestination = startDestination)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        // Scan inbox every time user opens the app
        val token = tokenHolder.token
        if (!token.isNullOrBlank()) {
            val hasSmsPermission = ContextCompat.checkSelfPermission(
                this, Manifest.permission.READ_SMS
            ) == PackageManager.PERMISSION_GRANTED
            if (hasSmsPermission) {
                triggerImmediateSync()
            }
        }
    }

    private fun triggerImmediateSync() {
        val syncWork = OneTimeWorkRequestBuilder<SmsSyncWorker>()
            .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        WorkManager.getInstance(this).enqueueUniqueWork(
            "inbox_scan",
            ExistingWorkPolicy.REPLACE,
            syncWork
        )
    }
}

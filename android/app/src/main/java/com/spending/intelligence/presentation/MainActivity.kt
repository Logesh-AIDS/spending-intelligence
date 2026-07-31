package com.spending.intelligence.presentation

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import androidx.navigation.compose.rememberNavController
import com.spending.intelligence.data.local.TokenDataStore
import com.spending.intelligence.data.local.TokenHolder
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.navigation.SpendingNavGraph
import com.spending.intelligence.presentation.theme.SpendingTheme
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject lateinit var tokenDataStore: TokenDataStore
    @Inject lateinit var tokenHolder: TokenHolder

    private val smsPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { /* permission result handled */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // CRITICAL: Restore token from DataStore into TokenHolder BEFORE any API call
        // Use runBlocking here intentionally — we need it before UI renders
        val savedToken = runBlocking { tokenDataStore.token.first() }
        if (!savedToken.isNullOrBlank()) {
            tokenHolder.token = savedToken
        }

        val startDestination = if (!savedToken.isNullOrBlank()) {
            Screen.Dashboard.route
        } else {
            Screen.Login.route
        }

        // Request SMS permissions
        smsPermissionLauncher.launch(
            arrayOf(
                Manifest.permission.RECEIVE_SMS,
                Manifest.permission.READ_SMS
            )
        )

        setContent {
            SpendingTheme {
                val navController = rememberNavController()
                SpendingNavGraph(
                    navController = navController,
                    startDestination = startDestination
                )
            }
        }
    }
}

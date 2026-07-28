package com.spending.intelligence.presentation

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.lifecycle.lifecycleScope
import androidx.navigation.compose.rememberNavController
import com.spending.intelligence.data.local.TokenDataStore
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

    @Inject
    lateinit var tokenDataStore: TokenDataStore

    // Request SMS permissions at launch
    private val smsPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        val granted = results.values.all { it }
        // Store permission status if needed
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Request SMS permissions (needed for automatic bank SMS detection)
        smsPermissionLauncher.launch(
            arrayOf(
                Manifest.permission.RECEIVE_SMS,
                Manifest.permission.READ_SMS
            )
        )

        // Determine start destination synchronously from stored token
        val hasToken = runBlocking { tokenDataStore.token.first() != null }
        val startDestination = if (hasToken) Screen.Dashboard.route else Screen.Login.route

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

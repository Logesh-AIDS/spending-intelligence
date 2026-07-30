package com.spending.intelligence.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.spending.intelligence.presentation.auth.LoginScreen
import com.spending.intelligence.presentation.auth.RegisterScreen
import com.spending.intelligence.presentation.dashboard.DashboardScreen
import com.spending.intelligence.presentation.transactions.TransactionsScreen
import com.spending.intelligence.presentation.analytics.AnalyticsScreen
import com.spending.intelligence.presentation.budgets.BudgetsScreen
import com.spending.intelligence.presentation.notifications.NotificationsScreen
import com.spending.intelligence.presentation.settings.SettingsScreen

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Register : Screen("register")
    object Dashboard : Screen("dashboard")
    object Transactions : Screen("transactions")
    object Analytics : Screen("analytics")
    object Budgets : Screen("budgets")
    object Notifications : Screen("notifications")
    object Settings : Screen("settings")
}

@Composable
fun SpendingNavGraph(
    navController: NavHostController,
    startDestination: String
) {
    NavHost(navController = navController, startDestination = startDestination) {

        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToRegister = { navController.navigate(Screen.Register.route) }
            )
        }

        composable(Screen.Register.route) {
            RegisterScreen(
                onRegisterSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
                },
                onNavigateToLogin = { navController.popBackStack() }
            )
        }

        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigate = { navController.navigate(it) }
            )
        }

        composable(Screen.Transactions.route) {
            TransactionsScreen(
                onBack = { navController.popBackStack() },
                onNavigate = { navController.navigate(it) }
            )
        }

        composable(Screen.Analytics.route) {
            AnalyticsScreen(
                onBack = { navController.popBackStack() },
                onNavigate = { navController.navigate(it) }
            )
        }

        composable(Screen.Budgets.route) {
            BudgetsScreen(
                onBack = { navController.popBackStack() },
                onNavigate = { navController.navigate(it) }
            )
        }

        composable(Screen.Notifications.route) {
            NotificationsScreen(onBack = { navController.popBackStack() })
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                onBack = { navController.popBackStack() },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
    }
}

package com.spending.intelligence.presentation.dashboard

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import com.spending.intelligence.navigation.Screen

data class NavItem(val route: String, val label: String, val icon: ImageVector)

val navItems = listOf(
    NavItem(Screen.Dashboard.route, "Home", Icons.Default.Home),
    NavItem(Screen.Transactions.route, "Transactions", Icons.Default.List),
    NavItem(Screen.Analytics.route, "Analytics", Icons.Default.BarChart),
    NavItem(Screen.Budgets.route, "Budgets", Icons.Default.Savings),
)

@Composable
fun BottomNavBar(currentRoute: String, onNavigate: (String) -> Unit) {
    NavigationBar {
        navItems.forEach { item ->
            NavigationBarItem(
                selected = currentRoute == item.route,
                onClick = { if (currentRoute != item.route) onNavigate(item.route) },
                icon = { Icon(item.icon, item.label) },
                label = { Text(item.label) }
            )
        }
    }
}

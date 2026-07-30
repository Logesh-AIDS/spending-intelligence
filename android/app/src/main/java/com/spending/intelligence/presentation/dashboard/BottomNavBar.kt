package com.spending.intelligence.presentation.dashboard

import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.presentation.theme.PrimaryBlue

data class NavItem(val route: String, val label: String, val icon: ImageVector)

val navItems = listOf(
    NavItem(Screen.Dashboard.route, "Home", Icons.Default.Home),
    NavItem(Screen.Transactions.route, "Transactions", Icons.Default.CreditCard),
    NavItem(Screen.Analytics.route, "Analytics", Icons.Default.BarChart),
    NavItem(Screen.Budgets.route, "Goals", Icons.Default.TrackChanges),
)

@Composable
fun BottomNavBar(currentRoute: String, onNavigate: (String) -> Unit) {
    NavigationBar(
        containerColor = Color.White,
        contentColor = PrimaryBlue,
        modifier = Modifier.height(64.dp)
    ) {
        navItems.forEach { item ->
            val selected = currentRoute == item.route
            NavigationBarItem(
                selected = selected,
                onClick = { if (currentRoute != item.route) onNavigate(item.route) },
                icon = {
                    Icon(item.icon, item.label,
                        modifier = Modifier.size(if (selected) 26.dp else 22.dp))
                },
                label = {
                    Text(item.label, fontSize = 10.sp,
                        fontWeight = if (selected) androidx.compose.ui.text.font.FontWeight.Bold
                        else androidx.compose.ui.text.font.FontWeight.Normal)
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = PrimaryBlue,
                    selectedTextColor = PrimaryBlue,
                    unselectedIconColor = Color(0xFF9BA8CC),
                    unselectedTextColor = Color(0xFF9BA8CC),
                    indicatorColor = Color(0xFFE8EEFF)
                )
            )
        }
    }
}

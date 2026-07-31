package com.spending.intelligence.presentation.dashboard

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
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
    // Shadow on top edge replaces the harsh divider line
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 16.dp,
                shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
                clip = false
            ),
        shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
        color = Color.White,
        tonalElevation = 0.dp
    ) {
        NavigationBar(
            containerColor = Color.Transparent,
            contentColor = PrimaryBlue,
            modifier = Modifier.height(68.dp),
            tonalElevation = 0.dp
        ) {
            navItems.forEach { item ->
                val selected = currentRoute == item.route
                NavigationBarItem(
                    selected = selected,
                    onClick = { if (currentRoute != item.route) onNavigate(item.route) },
                    icon = {
                        Icon(
                            item.icon,
                            contentDescription = item.label,
                            modifier = Modifier.size(if (selected) 24.dp else 22.dp)
                        )
                    },
                    label = {
                        Text(
                            item.label,
                            fontSize = 10.sp,
                            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
                        )
                    },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = PrimaryBlue,
                        selectedTextColor = PrimaryBlue,
                        unselectedIconColor = Color(0xFFB0BAD3),
                        unselectedTextColor = Color(0xFFB0BAD3),
                        indicatorColor = Color(0xFFE8EEFF)
                    )
                )
            }
        }
    }
}

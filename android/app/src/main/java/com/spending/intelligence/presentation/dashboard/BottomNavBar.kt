package com.spending.intelligence.presentation.dashboard

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
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
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 20.dp,
                shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
                clip = true,
                ambientColor = Color(0x30000000),
                spotColor = Color(0x20000000)
            )
            .clip(RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp))
            .background(Color.White)
            .padding(horizontal = 8.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            navItems.forEach { item ->
                val selected = currentRoute == item.route
                NavBarItem(
                    item = item,
                    selected = selected,
                    onClick = { if (!selected) onNavigate(item.route) }
                )
            }
        }
    }
}

@Composable
private fun NavBarItem(item: NavItem, selected: Boolean, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier
                .size(if (selected) 44.dp else 40.dp)
                .clip(CircleShape)
                .background(
                    if (selected) PrimaryBlue.copy(alpha = 0.12f)
                    else Color.Transparent
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = item.icon,
                contentDescription = item.label,
                tint = if (selected) PrimaryBlue else Color(0xFFB0BAD3),
                modifier = Modifier.size(if (selected) 24.dp else 22.dp)
            )
        }
        Spacer(Modifier.height(4.dp))
        Text(
            text = item.label,
            fontSize = 10.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
            color = if (selected) PrimaryBlue else Color(0xFFB0BAD3)
        )
        // Active dot indicator
        if (selected) {
            Spacer(Modifier.height(2.dp))
            Box(
                modifier = Modifier
                    .size(4.dp)
                    .clip(CircleShape)
                    .background(PrimaryBlue)
            )
        } else {
            Spacer(Modifier.height(6.dp))
        }
    }
}

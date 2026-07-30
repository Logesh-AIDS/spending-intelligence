package com.spending.intelligence.presentation.analytics

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.presentation.dashboard.BottomNavBar
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.presentation.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyticsScreen(
    onBack: () -> Unit,
    onNavigate: ((String) -> Unit)? = null,
    viewModel: AnalyticsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White),
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, null, tint = Color(0xFF0D1B4B))
                    }
                },
                title = {
                    Column {
                        Text("Analytics", fontWeight = FontWeight.Bold, fontSize = 20.sp,
                            color = Color(0xFF0D1B4B))
                        Text("Spending insights", fontSize = 12.sp, color = Color(0xFF6B7DB3))
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.load() }) {
                        Icon(Icons.Default.Refresh, null, tint = PrimaryBlue)
                    }
                }
            )
        },
        bottomBar = {
            onNavigate?.let {
                BottomNavBar(currentRoute = Screen.Analytics.route, onNavigate = it)
            }
        }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator(color = PrimaryBlue)
                    Spacer(Modifier.height(12.dp))
                    Text("Loading analytics...", color = Color(0xFF6B7DB3))
                }
            }
            state.error != null && state.categoryData == null -> Box(
                Modifier.fillMaxSize().padding(32.dp), Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("📊", fontSize = 48.sp)
                    Spacer(Modifier.height(12.dp))
                    Text("Could not load analytics", fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp, color = Color(0xFF0D1B4B))
                    Text(state.error!!, fontSize = 13.sp, color = Color(0xFF6B7DB3),
                        textAlign = TextAlign.Center)
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = { viewModel.load() },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
                        shape = RoundedCornerShape(12.dp)) {
                        Text("Retry")
                    }
                }
            }
            else -> LazyColumn(
                Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // ── Category Breakdown ──
                state.categoryData?.let { cat ->
                    item {
                        SectionCard("Spending by Category",
                            Icons.Default.PieChart, AccentPurple) {
                            if (cat.categories.isEmpty()) {
                                EmptyState("No category data yet")
                            } else {
                                cat.categories.take(6).forEach { c ->
                                    CategoryRow(c.category, c.totalSpent, c.percentage)
                                }
                                cat.highestCategory?.let { top ->
                                    Spacer(Modifier.height(8.dp))
                                    Surface(shape = RoundedCornerShape(8.dp),
                                        color = CardPurple) {
                                        Row(Modifier.fillMaxWidth().padding(10.dp),
                                            verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Default.TrendingUp, null,
                                                tint = AccentPurple, modifier = Modifier.size(16.dp))
                                            Spacer(Modifier.width(6.dp))
                                            Text("Top: $top", fontSize = 13.sp,
                                                color = AccentPurple, fontWeight = FontWeight.SemiBold)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // ── Financial Stats ──
                state.statistics?.let { s ->
                    item {
                        SectionCard("Financial Statistics",
                            Icons.Default.BarChart, PrimaryBlue) {
                            Row(Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                MiniStatCard("Total Txns",
                                    s.totalTransactions.toString(), AccentPurple,
                                    CardPurple, Modifier.weight(1f))
                                MiniStatCard("Avg Debit",
                                    "₹${s.avgDebitAmount.toLong()}", AccentRed,
                                    CardRed, Modifier.weight(1f))
                            }
                            Spacer(Modifier.height(12.dp))
                            Row(Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                MiniStatCard("Total Debits",
                                    "₹${s.totalDebitAmount.toLong()}", AccentRed,
                                    CardRed, Modifier.weight(1f))
                                MiniStatCard("Total Credits",
                                    "₹${s.totalCreditAmount.toLong()}", AccentGreen,
                                    CardGreen, Modifier.weight(1f))
                            }
                        }
                    }
                }

                // ── Spending Behaviour ──
                state.behaviour?.let { b ->
                    item {
                        SectionCard("Spending Behaviour",
                            Icons.Default.Psychology, AccentOrange) {
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                BehaviourRow(Icons.Default.TrendingUp, "Average", "₹${b.averageSpending.toLong()}", AccentGreen)
                                BehaviourRow(Icons.Default.BarChart, "Median", "₹${b.medianSpending.toLong()}", PrimaryBlue)
                                BehaviourRow(Icons.Default.ArrowUpward, "Highest", "₹${b.maxSpending.toLong()}", AccentRed)
                                BehaviourRow(Icons.Default.Weekend, "Weekend", "₹${b.weekendSpending.toLong()}", AccentOrange)
                                BehaviourRow(Icons.Default.Work, "Weekday", "₹${b.weekdaySpending.toLong()}", AccentPurple)
                                BehaviourRow(Icons.Default.CalendarMonth, "Most Active Day",
                                    b.mostActiveDay ?: "—", Color(0xFF6B7DB3))
                                BehaviourRow(Icons.Default.Speed, "Freq/Day",
                                    "${b.frequencyPerDay} txns", PrimaryBlue)
                            }
                        }
                    }
                }

                // Empty state if nothing loaded
                if (state.categoryData == null && state.behaviour == null && state.statistics == null && !state.isLoading) {
                    item {
                        Box(Modifier.fillMaxWidth().padding(32.dp), Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("📊", fontSize = 48.sp)
                                Spacer(Modifier.height(12.dp))
                                Text("No analytics data yet", fontWeight = FontWeight.SemiBold,
                                    fontSize = 16.sp, color = Color(0xFF0D1B4B))
                                Text("Add transactions to see insights",
                                    fontSize = 13.sp, color = Color(0xFF6B7DB3))
                            }
                        }
                    }
                }
            }
        }
    }
}

// ── Reusable components ───────────────────────────────────────────────────────

@Composable
private fun SectionCard(
    title: String, icon: ImageVector, color: Color, content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(36.dp).clip(CircleShape)
                    .background(color.copy(alpha = 0.12f)), Alignment.Center) {
                    Icon(icon, null, tint = color, modifier = Modifier.size(20.dp))
                }
                Spacer(Modifier.width(10.dp))
                Text(title, fontWeight = FontWeight.Bold, fontSize = 16.sp,
                    color = Color(0xFF0D1B4B))
            }
            Spacer(Modifier.height(14.dp))
            content()
        }
    }
}

@Composable
private fun CategoryRow(category: String, amount: Double, percentage: Double) {
    Column(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(category, fontSize = 13.sp, color = Color(0xFF0D1B4B))
            Row {
                Text("₹${amount.toLong()}", fontSize = 13.sp, fontWeight = FontWeight.SemiBold,
                    color = Color(0xFF0D1B4B))
                Spacer(Modifier.width(8.dp))
                Text("${percentage.toInt()}%", fontSize = 12.sp, color = Color(0xFF6B7DB3))
            }
        }
        Spacer(Modifier.height(3.dp))
        LinearProgressIndicator(
            progress = { (percentage / 100f).toFloat().coerceIn(0f, 1f) },
            modifier = Modifier.fillMaxWidth().height(5.dp).clip(RoundedCornerShape(3.dp)),
            color = categoryBarColor(category),
            trackColor = Color(0xFFEEF1FB)
        )
    }
}

@Composable
private fun MiniStatCard(label: String, value: String, color: Color, bg: Color, modifier: Modifier) {
    Surface(modifier = modifier, shape = RoundedCornerShape(12.dp), color = bg) {
        Column(Modifier.padding(12.dp)) {
            Text(value, fontWeight = FontWeight.Bold, fontSize = 18.sp, color = color)
            Text(label, fontSize = 11.sp, color = Color(0xFF6B7DB3))
        }
    }
}

@Composable
private fun BehaviourRow(icon: ImageVector, label: String, value: String, color: Color) {
    Row(
        Modifier.fillMaxWidth().padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, null, tint = color, modifier = Modifier.size(18.dp))
        Spacer(Modifier.width(10.dp))
        Text(label, Modifier.weight(1f), fontSize = 13.sp, color = Color(0xFF6B7DB3))
        Text(value, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = Color(0xFF0D1B4B))
    }
}

@Composable
private fun EmptyState(message: String) {
    Box(Modifier.fillMaxWidth().padding(16.dp), Alignment.Center) {
        Text(message, fontSize = 13.sp, color = Color(0xFF6B7DB3))
    }
}

private fun categoryBarColor(category: String): Color = when (category.lowercase()) {
    "food" -> Color(0xFFFF6B35)
    "shopping" -> Color(0xFF7C3AED)
    "travel" -> Color(0xFF00A3FF)
    "bills" -> Color(0xFFFF4D6A)
    "health" -> Color(0xFF00C896)
    "entertainment" -> Color(0xFFFFBF00)
    "education" -> Color(0xFF1A56DB)
    "salary" -> Color(0xFF00C896)
    else -> Color(0xFF6B7DB3)
}

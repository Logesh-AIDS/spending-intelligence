package com.spending.intelligence.presentation.dashboard

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.domain.model.Transaction
import com.spending.intelligence.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onNavigate: (String) -> Unit,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("SpendControl", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = { onNavigate(Screen.Notifications.route) }) {
                        Icon(Icons.Default.Notifications, contentDescription = "Notifications")
                    }
                    IconButton(onClick = { onNavigate(Screen.Settings.route) }) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                }
            )
        },
        bottomBar = { BottomNavBar(currentRoute = Screen.Dashboard.route, onNavigate = onNavigate) }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                CircularProgressIndicator()
            }
            state.error != null -> ErrorView(state.error!!) { viewModel.load() }
            else -> LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // ── Health Score ──
                state.healthScore?.let { h ->
                    item {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                                Text(h.grade, fontSize = 40.sp, fontWeight = FontWeight.Bold,
                                    color = gradeColor(h.grade))
                                Spacer(Modifier.width(16.dp))
                                Column {
                                    Text("Financial Health: ${h.score.toInt()}/100", fontWeight = FontWeight.SemiBold)
                                    Text(h.interpretation, fontSize = 12.sp,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                                }
                            }
                        }
                    }
                }

                // ── KPI Cards ──
                state.summary?.let { s ->
                    item {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            KpiCard("Balance", s.currentBalance?.let { "₹${it.toLong()}" } ?: "—",
                                modifier = Modifier.weight(1f))
                            KpiCard("Income", "₹${s.totalIncome.toLong()}",
                                valueColor = Color(0xFF10B981), modifier = Modifier.weight(1f))
                        }
                    }
                    item {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            KpiCard("Expenses", "₹${s.totalSpending.toLong()}",
                                valueColor = Color(0xFFEF4444), modifier = Modifier.weight(1f))
                            KpiCard("Savings", "${s.savingsPercentage.toInt()}%",
                                valueColor = if (s.savingsPercentage >= 20) Color(0xFF10B981) else Color(0xFFF59E0B),
                                modifier = Modifier.weight(1f))
                        }
                    }
                    item {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            KpiCard("Today", "₹${s.todaySpending.toLong()}", modifier = Modifier.weight(1f))
                            KpiCard("This Month", "₹${s.thisMonthSpending.toLong()}", modifier = Modifier.weight(1f))
                        }
                    }

                    // ── Recent Transactions ──
                    item {
                        Text("Recent Transactions", fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                    }
                    if (s.recentTransactions.isEmpty()) {
                        item {
                            Card(modifier = Modifier.fillMaxWidth()) {
                                Text("No transactions yet. Your bank SMS will be auto-detected.",
                                    modifier = Modifier.padding(16.dp),
                                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    } else {
                        items(s.recentTransactions) { txn -> TransactionRow(txn) }
                    }
                }
            }
        }
    }
}

@Composable
private fun KpiCard(label: String, value: String, valueColor: Color = Color.Unspecified, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Column(Modifier.padding(12.dp)) {
            Text(label, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(value, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = valueColor)
        }
    }
}

@Composable
private fun TransactionRow(txn: Transaction) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(txn.merchant ?: txn.bank, fontWeight = FontWeight.Medium)
                Text("${txn.category} · ${txn.date}", fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Text(txn.displayAmount,
                color = if (txn.isDebit) Color(0xFFEF4444) else Color(0xFF10B981),
                fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun ErrorView(message: String, onRetry: () -> Unit) {
    Column(Modifier.fillMaxSize(), Arrangement.Center, Alignment.CenterHorizontally) {
        Text("Failed to load", fontWeight = FontWeight.SemiBold)
        Text(message, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 13.sp)
        Spacer(Modifier.height(16.dp))
        Button(onClick = onRetry) { Text("Retry") }
    }
}

private fun gradeColor(grade: String) = when (grade) {
    "A" -> Color(0xFF10B981)
    "B" -> Color(0xFF3B82F6)
    "C" -> Color(0xFFF59E0B)
    else -> Color(0xFFEF4444)
}

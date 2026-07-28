package com.spending.intelligence.presentation.analytics

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyticsScreen(
    onBack: () -> Unit,
    viewModel: AnalyticsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Analytics") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, null) } }
            )
        }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
            else -> LazyColumn(
                Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Category breakdown
                state.categoryData?.let { cat ->
                    item {
                        Card(Modifier.fillMaxWidth()) {
                            Column(Modifier.padding(16.dp)) {
                                Text("Spending by Category", fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                                Spacer(Modifier.height(8.dp))
                                cat.categories.take(6).forEach { c ->
                                    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically) {
                                        Text(c.category, Modifier.weight(1f), fontSize = 13.sp)
                                        LinearProgressIndicator(
                                            progress = { (c.percentage / 100f).toFloat() },
                                            modifier = Modifier.width(80.dp).height(6.dp),
                                            color = MaterialTheme.colorScheme.primary
                                        )
                                        Spacer(Modifier.width(8.dp))
                                        Text("${c.percentage.toInt()}%", fontSize = 12.sp,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                }
                            }
                        }
                    }
                }

                // Behaviour stats
                state.behaviour?.let { b ->
                    item {
                        Card(Modifier.fillMaxWidth()) {
                            Column(Modifier.padding(16.dp)) {
                                Text("Spending Behaviour", fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                                Spacer(Modifier.height(8.dp))
                                BehaviourRow("Average Transaction", "₹${b.averageSpending.toLong()}")
                                BehaviourRow("Median Transaction", "₹${b.medianSpending.toLong()}")
                                BehaviourRow("Max Transaction", "₹${b.maxSpending.toLong()}")
                                BehaviourRow("Weekend Spending", "₹${b.weekendSpending.toLong()}")
                                BehaviourRow("Most Active Day", b.mostActiveDay ?: "—")
                                BehaviourRow("Transactions/Day", b.frequencyPerDay.toString())
                            }
                        }
                    }
                }

                // Stats
                state.statistics?.let { s ->
                    item {
                        Card(Modifier.fillMaxWidth()) {
                            Column(Modifier.padding(16.dp)) {
                                Text("Financial Statistics", fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
                                Spacer(Modifier.height(8.dp))
                                BehaviourRow("Total Transactions", s.totalTransactions.toString())
                                BehaviourRow("Total Debits", "₹${s.totalDebitAmount.toLong()}")
                                BehaviourRow("Total Credits", "₹${s.totalCreditAmount.toLong()}")
                                BehaviourRow("Avg Debit", "₹${s.avgDebitAmount.toLong()}")
                                BehaviourRow("Highest Debit", s.highestDebit?.let { "₹${it.toLong()}" } ?: "—")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun BehaviourRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
        Text(label, Modifier.weight(1f), fontSize = 13.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, fontWeight = FontWeight.Medium, fontSize = 13.sp)
    }
}

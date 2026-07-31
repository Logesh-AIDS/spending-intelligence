package com.spending.intelligence.presentation.transactions

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.domain.model.Transaction
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.presentation.dashboard.BottomNavBar
import com.spending.intelligence.presentation.theme.*
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TransactionsScreen(
    onBack: () -> Unit,
    onNavigate: ((String) -> Unit)? = null,
    viewModel: TransactionsViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    val search by viewModel.searchQuery.collectAsState()
    var deleteTarget by remember { mutableStateOf<Int?>(null) }
    var filterType by remember { mutableStateOf<String?>(null) }

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
                        Text("Transactions", fontWeight = FontWeight.Bold, fontSize = 20.sp,
                            color = Color(0xFF0D1B4B))
                        Text("${state.transactions.size} records", fontSize = 12.sp,
                            color = Color(0xFF6B7DB3))
                    }
                },
                actions = {
                    if (state.isSyncing) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp).padding(end = 12.dp),
                            strokeWidth = 2.dp, color = PrimaryBlue
                        )
                    } else {
                        IconButton(onClick = { viewModel.sync() }) {
                            Icon(Icons.Default.Sync, null, tint = PrimaryBlue)
                        }
                    }
                }
            )
        },
        bottomBar = {
            onNavigate?.let {
                BottomNavBar(currentRoute = Screen.Transactions.route, onNavigate = it)
            }
        }
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {

            // Search bar
            OutlinedTextField(
                value = search, onValueChange = { viewModel.setSearch(it) },
                placeholder = { Text("Search merchant, category...") },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = Color(0xFF6B7DB3)) },
                trailingIcon = {
                    if (search.isNotBlank()) IconButton(onClick = { viewModel.setSearch("") }) {
                        Icon(Icons.Default.Clear, null, tint = Color(0xFF6B7DB3))
                    }
                },
                singleLine = true,
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                shape = RoundedCornerShape(14.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = PrimaryBlue,
                    unfocusedBorderColor = Color(0xFFD0D8F0),
                    focusedContainerColor = Color.White,
                    unfocusedContainerColor = Color.White
                )
            )

            // Filter chips
            Row(
                Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(null to "All", "Debit" to "Debits", "Credit" to "Credits").forEach { (type, label) ->
                    val selected = filterType == type
                    FilterChip(
                        selected = selected,
                        onClick = { filterType = if (filterType == type) null else type },
                        label = { Text(label, fontSize = 12.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = when (type) {
                                "Debit" -> CardRed
                                "Credit" -> CardGreen
                                else -> CardBlue
                            },
                            selectedLabelColor = when (type) {
                                "Debit" -> AccentRed
                                "Credit" -> AccentGreen
                                else -> PrimaryBlue
                            }
                        )
                    )
                }
            }

            val filtered = when (filterType) {
                "Debit" -> state.transactions.filter { it.isDebit }
                "Credit" -> state.transactions.filter { it.isCredit }
                else -> state.transactions
            }.let { list ->
                if (search.isNotBlank()) list.filter {
                    it.merchant?.contains(search, ignoreCase = true) == true ||
                    it.category.contains(search, ignoreCase = true) ||
                    it.bank.contains(search, ignoreCase = true)
                } else list
            }

            if (filtered.isEmpty()) {
                Box(Modifier.fillMaxSize(), Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("💳", fontSize = 48.sp)
                        Spacer(Modifier.height(12.dp))
                        Text("No transactions found", fontWeight = FontWeight.SemiBold,
                            fontSize = 16.sp, color = Color(0xFF0D1B4B))
                    }
                }
            } else {
                // Group by month
                val grouped = filtered.groupBy { getMonthLabel(it.date) }
                val sortedMonths = grouped.keys.sortedByDescending { parseMonthForSort(it) }

                LazyColumn(
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    sortedMonths.forEach { month ->
                        val monthTxns = grouped[month] ?: emptyList()
                        val monthTotal = monthTxns.filter { it.isDebit }.sumOf { it.amount }
                        val monthIncome = monthTxns.filter { it.isCredit }.sumOf { it.amount }

                        // Month header
                        item(key = "header_$month") {
                            Spacer(Modifier.height(8.dp))
                            Row(
                                Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(month, fontWeight = FontWeight.Bold, fontSize = 15.sp,
                                    color = Color(0xFF0D1B4B))
                                Column(horizontalAlignment = Alignment.End) {
                                    if (monthIncome > 0) Text("+₹${monthIncome.toLong()}",
                                        fontSize = 12.sp, color = AccentGreen, fontWeight = FontWeight.SemiBold)
                                    Text("-₹${monthTotal.toLong()}", fontSize = 12.sp,
                                        color = AccentRed, fontWeight = FontWeight.SemiBold)
                                }
                            }
                            Spacer(Modifier.height(6.dp))
                        }

                        // Transactions for this month
                        items(monthTxns, key = { it.id }) { txn ->
                            TransactionCard(txn, onDelete = { deleteTarget = txn.id })
                            Spacer(Modifier.height(4.dp))
                        }
                    }
                }
            }
        }
    }

    deleteTarget?.let { id ->
        AlertDialog(
            onDismissRequest = { deleteTarget = null },
            containerColor = Color.White,
            shape = RoundedCornerShape(20.dp),
            icon = {
                Icon(Icons.Default.DeleteForever, null, tint = AccentRed,
                    modifier = Modifier.size(32.dp))
            },
            title = { Text("Delete Transaction", fontWeight = FontWeight.Bold) },
            text = { Text("This cannot be undone.", color = Color(0xFF6B7DB3)) },
            confirmButton = {
                Button(
                    onClick = { viewModel.delete(id); deleteTarget = null },
                    colors = ButtonDefaults.buttonColors(containerColor = AccentRed),
                    shape = RoundedCornerShape(10.dp)
                ) { Text("Delete") }
            },
            dismissButton = {
                OutlinedButton(onClick = { deleteTarget = null },
                    shape = RoundedCornerShape(10.dp)) { Text("Cancel") }
            }
        )
    }
}

@Composable
private fun TransactionCard(transaction: Transaction, onDelete: () -> Unit) {
    val isDebit = transaction.isDebit
    val color = if (isDebit) AccentRed else AccentGreen
    val bgColor = if (isDebit) Color(0xFFFFF0F2) else Color(0xFFF0FBF7)
    val categoryEmoji = getCategoryEmoji(transaction.category)

    Card(
        modifier = Modifier.fillMaxWidth().shadow(2.dp, RoundedCornerShape(14.dp)),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            // Category emoji circle
            Box(
                Modifier.size(44.dp).clip(CircleShape).background(bgColor),
                Alignment.Center
            ) {
                Text(categoryEmoji, fontSize = 20.sp)
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    transaction.merchant ?: transaction.bank,
                    fontWeight = FontWeight.SemiBold, fontSize = 14.sp,
                    color = Color(0xFF0D1B4B)
                )
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    Surface(shape = RoundedCornerShape(4.dp), color = bgColor) {
                        Text(
                            transaction.category.replaceFirstChar { it.uppercase() },
                            fontSize = 10.sp, color = color,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    Text("·", color = Color(0xFF6B7DB3), fontSize = 10.sp)
                    Text(transaction.date, fontSize = 11.sp, color = Color(0xFF6B7DB3))
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    "${if (isDebit) "-" else "+"}₹${transaction.amount.toLong()}",
                    color = color, fontWeight = FontWeight.Bold, fontSize = 15.sp
                )
                transaction.balance?.let {
                    Text("₹${it.toLong()}", fontSize = 10.sp, color = Color(0xFF6B7DB3))
                }
            }
            Spacer(Modifier.width(4.dp))
            IconButton(onClick = onDelete, modifier = Modifier.size(28.dp)) {
                Icon(Icons.Default.Delete, null, tint = Color(0xFFDDE0EE),
                    modifier = Modifier.size(15.dp))
            }
        }
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

private fun getMonthLabel(dateStr: String): String {
    return try {
        val sdf = SimpleDateFormat("dd/MM/yy", Locale.getDefault())
        val date = sdf.parse(dateStr) ?: return dateStr
        val cal = Calendar.getInstance().apply { time = date }
        val months = listOf("Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec")
        "${months[cal.get(Calendar.MONTH)]} ${cal.get(Calendar.YEAR)}"
    } catch (e: Exception) { dateStr }
}

private fun parseMonthForSort(label: String): String {
    return try {
        val sdf = SimpleDateFormat("MMM yyyy", Locale.getDefault())
        val date = sdf.parse(label) ?: return label
        SimpleDateFormat("yyyyMM", Locale.getDefault()).format(date)
    } catch (e: Exception) { label }
}

private fun getCategoryEmoji(category: String): String = when (category.lowercase()) {
    "food" -> "🍽️"
    "shopping" -> "🛍️"
    "travel" -> "🚗"
    "bills" -> "⚡"
    "health" -> "🏥"
    "entertainment" -> "🎬"
    "education" -> "📚"
    "salary" -> "💰"
    "investment" -> "📈"
    "transfer" -> "↔️"
    else -> "💳"
}

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
                        CircularProgressIndicator(modifier = Modifier.size(20.dp).padding(end = 12.dp),
                            strokeWidth = 2.dp, color = PrimaryBlue)
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
                placeholder = { Text("Search merchant, bank, category...") },
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
                    focusedBorderColor = PrimaryBlue, unfocusedBorderColor = Color(0xFFD0D8F0),
                    focusedContainerColor = Color.White, unfocusedContainerColor = Color.White
                )
            )

            // Filter chips
            Row(Modifier.padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(filterType == null, { filterType = null }, label = { Text("All") })
                FilterChip(filterType == "Debit", { filterType = if (filterType == "Debit") null else "Debit" },
                    label = { Text("Debits") }, colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = CardRed, selectedLabelColor = AccentRed))
                FilterChip(filterType == "Credit", { filterType = if (filterType == "Credit") null else "Credit" },
                    label = { Text("Credits") }, colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = CardGreen, selectedLabelColor = AccentGreen))
            }

            Spacer(Modifier.height(4.dp))

            state.error?.let { err ->
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                        .clip(RoundedCornerShape(10.dp)).background(CardRed).padding(12.dp)
                ) {
                    Icon(Icons.Default.Warning, null, tint = AccentRed, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text(err, color = AccentRed, fontSize = 13.sp)
                }
            }

            val filtered = if (filterType != null)
                state.transactions.filter { it.transactionType == filterType }
            else state.transactions

            if (filtered.isEmpty()) {
                Box(Modifier.fillMaxSize(), Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("💳", fontSize = 48.sp)
                        Spacer(Modifier.height(12.dp))
                        Text("No transactions found", fontWeight = FontWeight.SemiBold,
                            fontSize = 16.sp, color = Color(0xFF0D1B4B))
                        Text("Bank SMS are auto-detected", fontSize = 13.sp, color = Color(0xFF6B7DB3))
                    }
                }
            } else {
                LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(filtered, key = { it.id }) { txn ->
                        TransactionCard(txn, onDelete = { deleteTarget = txn.id })
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
            icon = { Icon(Icons.Default.DeleteForever, null, tint = AccentRed, modifier = Modifier.size(32.dp)) },
            title = { Text("Delete Transaction", fontWeight = FontWeight.Bold) },
            text = { Text("This action cannot be undone.", color = Color(0xFF6B7DB3)) },
            confirmButton = {
                Button(onClick = { viewModel.delete(id); deleteTarget = null },
                    colors = ButtonDefaults.buttonColors(containerColor = AccentRed),
                    shape = RoundedCornerShape(10.dp)) { Text("Delete") }
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

    Card(
        modifier = Modifier.fillMaxWidth().shadow(3.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier.size(44.dp).clip(CircleShape).background(bgColor),
                Alignment.Center
            ) {
                Text(if (isDebit) "↑" else "↓", fontSize = 20.sp, color = color,
                    fontWeight = FontWeight.ExtraBold)
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(transaction.merchant ?: transaction.bank, fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp, color = Color(0xFF0D1B4B))
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    Surface(shape = RoundedCornerShape(4.dp), color = bgColor) {
                        Text(transaction.category, fontSize = 10.sp, color = color,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                    }
                    Text("·", color = Color(0xFF6B7DB3), fontSize = 11.sp)
                    Text(transaction.date, fontSize = 11.sp, color = Color(0xFF6B7DB3))
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text("${if (isDebit) "-" else "+"}₹${transaction.amount.toLong()}",
                    color = color, fontWeight = FontWeight.Bold, fontSize = 15.sp)
                transaction.balance?.let {
                    Text("₹${it.toLong()}", fontSize = 10.sp, color = Color(0xFF6B7DB3))
                }
            }
            Spacer(Modifier.width(4.dp))
            IconButton(onClick = onDelete, modifier = Modifier.size(32.dp)) {
                Icon(Icons.Default.Delete, null, tint = Color(0xFFCCD0E0), modifier = Modifier.size(16.dp))
            }
        }
    }
}

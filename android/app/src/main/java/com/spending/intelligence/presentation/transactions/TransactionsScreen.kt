package com.spending.intelligence.presentation.transactions

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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TransactionsScreen(
    onBack: () -> Unit,
    viewModel: TransactionsViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    val search by viewModel.searchQuery.collectAsState()
    var deleteTarget by remember { mutableStateOf<Int?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Transactions") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, null) } },
                actions = {
                    if (state.isSyncing) CircularProgressIndicator(modifier = Modifier.size(20.dp).padding(end = 8.dp), strokeWidth = 2.dp)
                    else IconButton(onClick = { viewModel.sync() }) { Icon(Icons.Default.Refresh, "Sync") }
                }
            )
        }
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {
            // Search bar
            OutlinedTextField(
                value = search,
                onValueChange = { viewModel.setSearch(it) },
                placeholder = { Text("Search merchant, bank...") },
                leadingIcon = { Icon(Icons.Default.Search, null) },
                trailingIcon = {
                    if (search.isNotBlank()) IconButton(onClick = { viewModel.setSearch("") }) {
                        Icon(Icons.Default.Clear, null)
                    }
                },
                singleLine = true,
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)
            )

            state.error?.let { err ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)
                ) {
                    Text(err, Modifier.padding(12.dp), color = MaterialTheme.colorScheme.onErrorContainer)
                }
            }

            if (state.transactions.isEmpty()) {
                Box(Modifier.fillMaxSize(), Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Receipt, null, modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(Modifier.height(16.dp))
                        Text("No transactions yet", fontWeight = FontWeight.SemiBold)
                        Text("Bank SMS will be auto-detected", fontSize = 13.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            } else {
                LazyColumn(contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(state.transactions, key = { it.id }) { txn ->
                        TransactionCard(
                            transaction = txn,
                            onDelete = { deleteTarget = txn.id }
                        )
                    }
                }
            }
        }
    }

    deleteTarget?.let { id ->
        AlertDialog(
            onDismissRequest = { deleteTarget = null },
            title = { Text("Delete Transaction") },
            text = { Text("This cannot be undone.") },
            confirmButton = {
                TextButton(onClick = { viewModel.delete(id); deleteTarget = null }) {
                    Text("Delete", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = { TextButton(onClick = { deleteTarget = null }) { Text("Cancel") } }
        )
    }
}

@Composable
private fun TransactionCard(transaction: Transaction, onDelete: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            // Type indicator
            Surface(
                shape = MaterialTheme.shapes.small,
                color = if (transaction.isDebit) Color(0xFFFFEBEB) else Color(0xFFE8F5E9),
                modifier = Modifier.size(40.dp)
            ) {
                Box(Modifier.fillMaxSize(), Alignment.Center) {
                    Text(if (transaction.isDebit) "↓" else "↑", fontSize = 18.sp,
                        color = if (transaction.isDebit) Color(0xFFEF4444) else Color(0xFF10B981))
                }
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(transaction.merchant ?: transaction.bank, fontWeight = FontWeight.Medium)
                Text("${transaction.category} · ${transaction.date}", fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                transaction.balance?.let {
                    Text("Bal: ₹${it.toLong()}", fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(transaction.displayAmount,
                    color = if (transaction.isDebit) Color(0xFFEF4444) else Color(0xFF10B981),
                    fontWeight = FontWeight.SemiBold)
                IconButton(onClick = onDelete, modifier = Modifier.size(24.dp)) {
                    Icon(Icons.Default.Delete, null, tint = MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(16.dp))
                }
            }
        }
    }
}

package com.spending.intelligence.presentation.dashboard

import androidx.compose.animation.core.*
import androidx.compose.foundation.*
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
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.*
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.domain.model.DashboardSummary
import com.spending.intelligence.domain.model.HealthScore
import com.spending.intelligence.domain.model.Transaction
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.presentation.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onNavigate: (String) -> Unit,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        containerColor = BackgroundLight,
        topBar = { DashboardTopBar(onNavigate) },
        bottomBar = { BottomNavBar(currentRoute = Screen.Dashboard.route, onNavigate = onNavigate) }
    ) { padding ->
        when {
            state.isLoading -> LoadingScreen()
            state.error != null -> ErrorScreen(state.error!!) { viewModel.load() }
            state.summary != null -> DashboardContent(
                summary = state.summary!!,
                healthScore = state.healthScore,
                padding = padding,
                onNavigate = onNavigate
            )
            else -> ErrorScreen("No data") { viewModel.load() }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DashboardTopBar(onNavigate: (String) -> Unit) {
    TopAppBar(
        colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.Transparent),
        title = {
            Column {
                Text("SpendControl", fontWeight = FontWeight.Bold, fontSize = 22.sp,
                    color = Color(0xFF0D1B4B))
                Text("Your financial overview", fontSize = 12.sp, color = Color(0xFF6B7DB3))
            }
        },
        actions = {
            IconButton(onClick = { onNavigate(Screen.Notifications.route) }) {
                Icon(Icons.Default.Notifications, null, tint = PrimaryBlue)
            }
            IconButton(onClick = { onNavigate(Screen.Settings.route) }) {
                Icon(Icons.Default.AccountCircle, null, tint = PrimaryBlue)
            }
        }
    )
}

@Composable
private fun DashboardContent(
    summary: DashboardSummary,
    healthScore: HealthScore?,
    padding: PaddingValues,
    onNavigate: (String) -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(padding),
        contentPadding = PaddingValues(bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(0.dp)
    ) {
        // ── Hero Balance Card ──
        item { HeroBalanceCard(summary) }

        // ── Stats Row ──
        item { StatsRow(summary) }

        // ── Health Score ──
        healthScore?.let { item { HealthScoreCard(it) } }

        // ── Period Spending ──
        item { PeriodSpendingSection(summary) }

        // ── Recent Transactions ──
        item {
            Spacer(Modifier.height(8.dp))
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Recent Transactions", fontWeight = FontWeight.Bold, fontSize = 18.sp,
                    color = Color(0xFF0D1B4B))
                TextButton(onClick = { onNavigate(Screen.Transactions.route) }) {
                    Text("See All", color = PrimaryBlue, fontSize = 13.sp)
                }
            }
        }

        if (summary.recentTransactions.isEmpty()) {
            item { EmptyTransactionsCard() }
        } else {
            items(summary.recentTransactions) { txn ->
                TransactionItem(txn)
            }
        }
    }
}

// ── Hero Balance Card with gradient ──────────────────────────────────────────

@Composable
private fun HeroBalanceCard(summary: DashboardSummary) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF0F3460),   // deep navy
                        Color(0xFF16213E),   // dark blue
                        Color(0xFF1A1A2E)    // very dark blue-black
                    ),
                    start = androidx.compose.ui.geometry.Offset(0f, 0f),
                    end = androidx.compose.ui.geometry.Offset(Float.POSITIVE_INFINITY, Float.POSITIVE_INFINITY)
                )
            )
            .padding(24.dp)
    ) {
        // Decorative circle — subtle background element
        Box(
            modifier = Modifier
                .size(160.dp)
                .align(Alignment.TopEnd)
                .clip(CircleShape)
                .background(Color.White.copy(alpha = 0.04f))
        )

        Column {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("💳", fontSize = 16.sp)
                Spacer(Modifier.width(6.dp))
                Text("Current Balance", color = Color.White.copy(alpha = 0.7f), fontSize = 13.sp)
            }
            Spacer(Modifier.height(6.dp))
            Text(
                text = summary.currentBalance?.let { "₹${formatAmount(it)}" } ?: "—",
                color = Color.White,
                fontSize = 38.sp,
                fontWeight = FontWeight.ExtraBold
            )
            Spacer(Modifier.height(20.dp))

            // Divider
            HorizontalDivider(color = Color.White.copy(alpha = 0.15f), thickness = 1.dp)
            Spacer(Modifier.height(16.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(32.dp)) {
                MiniStat("Income", "₹${formatAmount(summary.totalIncome)}", Color(0xFF4ADE80))
                MiniStat("Expenses", "₹${formatAmount(summary.totalSpending)}", Color(0xFFFF7096))
                MiniStat("Savings", "${summary.savingsPercentage.toInt()}%",
                    if (summary.savingsPercentage >= 20) Color(0xFF4ADE80) else Color(0xFFFFB347))
            }
        }
    }
}

@Composable
private fun MiniStat(label: String, value: String, color: Color) {
    Column {
        Text(label, color = Color.White.copy(alpha = 0.7f), fontSize = 11.sp)
        Text(value, color = color, fontSize = 15.sp, fontWeight = FontWeight.Bold)
    }
}

// ── Stats Row ─────────────────────────────────────────────────────────────────

@Composable
private fun StatsRow(summary: DashboardSummary) {
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        StatCard("Today", "₹${formatAmount(summary.todaySpending)}",
            Icons.Default.Today, AccentOrange, CardRed, Modifier.weight(1f))
        StatCard("This Week", "₹${formatAmount(summary.thisWeekSpending)}",
            Icons.Default.DateRange, PrimaryBlue, CardBlue, Modifier.weight(1f))
        StatCard("Transactions", summary.totalTransactions.toString(),
            Icons.Default.Receipt, AccentPurple, CardPurple, Modifier.weight(1f))
    }
}

@Composable
private fun StatCard(
    label: String, value: String, icon: ImageVector,
    color: Color, bgColor: Color, modifier: Modifier
) {
    Card(
        modifier = modifier.shadow(4.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor)
    ) {
        Column(
            Modifier.padding(12.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Box(
                Modifier.size(36.dp).clip(CircleShape)
                    .background(color.copy(alpha = 0.15f)),
                Alignment.Center
            ) {
                Icon(icon, null, tint = color, modifier = Modifier.size(20.dp))
            }
            Spacer(Modifier.height(8.dp))
            Text(value, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = color)
            Text(label, fontSize = 11.sp, color = Color(0xFF6B7DB3))
        }
    }
}

// ── Health Score Card ─────────────────────────────────────────────────────────

@Composable
private fun HealthScoreCard(score: HealthScore) {
    val gradeColor = when (score.grade) {
        "A" -> AccentGreen; "B" -> PrimaryBlue; "C" -> AccentOrange; else -> AccentRed
    }
    val gradeBg = when (score.grade) {
        "A" -> CardGreen; "B" -> CardBlue; "C" -> Color(0xFFFFF3E0); else -> CardRed
    }

    Card(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)
            .shadow(4.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            // Grade circle
            Box(
                Modifier.size(64.dp).clip(CircleShape).background(gradeBg),
                Alignment.Center
            ) {
                Text(score.grade, fontSize = 28.sp, fontWeight = FontWeight.ExtraBold,
                    color = gradeColor)
            }
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Text("Financial Health", fontWeight = FontWeight.Bold, fontSize = 16.sp,
                    color = Color(0xFF0D1B4B))
                Spacer(Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { (score.score / 100f).toFloat() },
                    modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                    color = gradeColor,
                    trackColor = Color(0xFFEEF1FB)
                )
                Spacer(Modifier.height(4.dp))
                Text("${score.score.toInt()}/100 — ${score.interpretation}",
                    fontSize = 12.sp, color = Color(0xFF6B7DB3), maxLines = 2)
            }
        }
        if (score.improvementTips.isNotEmpty()) {
            Divider(color = Color(0xFFEEF1FB), modifier = Modifier.padding(horizontal = 16.dp))
            Row(Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) {
                Icon(Icons.Default.Lightbulb, null, tint = AccentOrange,
                    modifier = Modifier.size(16.dp).padding(top = 2.dp))
                Spacer(Modifier.width(6.dp))
                Text(score.improvementTips.first(), fontSize = 12.sp,
                    color = Color(0xFF6B7DB3), lineHeight = 18.sp)
            }
        }
    }
}

// ── Period Spending ───────────────────────────────────────────────────────────

@Composable
private fun PeriodSpendingSection(summary: DashboardSummary) {
    Column(Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
        Text("Spending Overview", fontWeight = FontWeight.Bold, fontSize = 18.sp,
            color = Color(0xFF0D1B4B))
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PeriodCard("This Month", summary.thisMonthSpending,
                summary.avgDailySpending * 30, PrimaryBlue, Modifier.weight(1f))
            PeriodCard("Daily Avg", summary.avgDailySpending,
                null, AccentGreen, Modifier.weight(1f))
        }
    }
}

@Composable
private fun PeriodCard(
    label: String, amount: Double, budget: Double?,
    color: Color, modifier: Modifier
) {
    val progress = if (budget != null && budget > 0) (amount / budget).coerceIn(0.0, 1.0) else null

    Card(
        modifier = modifier.shadow(4.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(Modifier.padding(14.dp)) {
            Text(label, fontSize = 12.sp, color = Color(0xFF6B7DB3))
            Spacer(Modifier.height(4.dp))
            Text("₹${formatAmount(amount)}", fontWeight = FontWeight.Bold,
                fontSize = 20.sp, color = color)
            progress?.let { p ->
                Spacer(Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { p.toFloat() },
                    modifier = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)),
                    color = if (p > 0.85) AccentRed else color,
                    trackColor = Color(0xFFEEF1FB)
                )
                Text("${(p * 100).toInt()}% of budget", fontSize = 10.sp,
                    color = Color(0xFF6B7DB3), modifier = Modifier.padding(top = 2.dp))
            }
        }
    }
}

// ── Transaction Item ──────────────────────────────────────────────────────────

@Composable
private fun TransactionItem(txn: Transaction) {
    val isDebit = txn.isDebit
    val categoryIcon = categoryIcon(txn.category)
    val categoryColor = categoryColor(txn.category)

    Card(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
            .shadow(2.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(
            Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Category icon circle
            Box(
                Modifier.size(46.dp).clip(CircleShape)
                    .background(categoryColor.copy(alpha = 0.15f)),
                Alignment.Center
            ) {
                Icon(categoryIcon, null, tint = categoryColor, modifier = Modifier.size(22.dp))
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(txn.merchant ?: txn.bank, fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp, color = Color(0xFF0D1B4B))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(txn.category, fontSize = 11.sp, color = Color(0xFF6B7DB3))
                    Text(" · ", fontSize = 11.sp, color = Color(0xFF6B7DB3))
                    Text(txn.date, fontSize = 11.sp, color = Color(0xFF6B7DB3))
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "${if (isDebit) "-" else "+"}₹${formatAmount(txn.amount)}",
                    color = if (isDebit) AccentRed else AccentGreen,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp
                )
                txn.balance?.let {
                    Text("Bal: ₹${formatAmount(it)}", fontSize = 10.sp,
                        color = Color(0xFF6B7DB3))
                }
            }
        }
    }
}

// ── Empty & Loading states ────────────────────────────────────────────────────

@Composable
private fun EmptyTransactionsCard() {
    Card(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            Modifier.fillMaxWidth().padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("💳", fontSize = 40.sp)
            Spacer(Modifier.height(12.dp))
            Text("No transactions yet", fontWeight = FontWeight.SemiBold,
                fontSize = 16.sp, color = Color(0xFF0D1B4B))
            Text("Bank SMS will be auto-detected", fontSize = 13.sp,
                color = Color(0xFF6B7DB3), textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun LoadingScreen() {
    Box(Modifier.fillMaxSize(), Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator(color = PrimaryBlue, strokeWidth = 3.dp)
            Spacer(Modifier.height(12.dp))
            Text("Loading your finances...", color = Color(0xFF6B7DB3), fontSize = 14.sp)
        }
    }
}

@Composable
private fun ErrorScreen(message: String, onRetry: () -> Unit) {
    Box(Modifier.fillMaxSize(), Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(32.dp)) {
            Text("⚠️", fontSize = 48.sp)
            Spacer(Modifier.height(16.dp))
            Text("Something went wrong", fontWeight = FontWeight.Bold, fontSize = 18.sp,
                color = Color(0xFF0D1B4B))
            Spacer(Modifier.height(8.dp))
            Text(message, fontSize = 13.sp, color = Color(0xFF6B7DB3),
                textAlign = TextAlign.Center)
            Spacer(Modifier.height(24.dp))
            Button(
                onClick = onRetry,
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Refresh, null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(6.dp))
                Text("Retry")
            }
        }
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

private fun formatAmount(amount: Double): String {
    return if (amount >= 1000) {
        val formatted = amount.toLong()
        val str = formatted.toString()
        buildString {
            val len = str.length
            str.forEachIndexed { i, c ->
                if (i > 0) {
                    val pos = len - i
                    if (pos == 3 || (pos > 3 && (pos - 3) % 2 == 0)) append(',')
                }
                append(c)
            }
        }
    } else {
        String.format("%.0f", amount)
    }
}

private fun categoryIcon(category: String): ImageVector = when (category.lowercase()) {
    "food" -> Icons.Default.Restaurant
    "shopping" -> Icons.Default.ShoppingBag
    "travel" -> Icons.Default.DirectionsCar
    "bills" -> Icons.Default.Receipt
    "health" -> Icons.Default.LocalHospital
    "entertainment" -> Icons.Default.Movie
    "education" -> Icons.Default.School
    "salary" -> Icons.Default.AccountBalance
    else -> Icons.Default.Payment
}

private fun categoryColor(category: String): Color = when (category.lowercase()) {
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

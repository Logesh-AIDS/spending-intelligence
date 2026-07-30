package com.spending.intelligence.presentation.budgets

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
import com.spending.intelligence.domain.model.Goal
import com.spending.intelligence.navigation.Screen
import com.spending.intelligence.presentation.dashboard.BottomNavBar
import com.spending.intelligence.presentation.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BudgetsScreen(
    onBack: () -> Unit,
    onNavigate: ((String) -> Unit)? = null,
    viewModel: BudgetsViewModel = hiltViewModel()
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
                        Text("Budget Goals", fontWeight = FontWeight.Bold,
                            fontSize = 20.sp, color = Color(0xFF0D1B4B))
                        Text("${state.goals.size} active goals", fontSize = 12.sp,
                            color = Color(0xFF6B7DB3))
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
                BottomNavBar(currentRoute = Screen.Budgets.route, onNavigate = it)
            }
        }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                CircularProgressIndicator(color = PrimaryBlue)
            }
            state.goals.isEmpty() -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(32.dp)) {
                    Text("🎯", fontSize = 48.sp)
                    Spacer(Modifier.height(12.dp))
                    Text("No budget goals yet", fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp, color = Color(0xFF0D1B4B))
                    Text("Create goals in the web app to track them here",
                        fontSize = 13.sp, color = Color(0xFF6B7DB3))
                }
            }
            else -> LazyColumn(
                Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(state.goals) { goal -> GoalCard(goal) }
            }
        }
    }
}

@Composable
private fun GoalCard(goal: Goal) {
    val predictionColor = when (goal.aiPrediction) {
        "achieved" -> AccentGreen
        "on_track" -> PrimaryBlue
        "at_risk" -> AccentOrange
        "failed" -> AccentRed
        else -> Color(0xFF6B7DB3)
    }
    val predictionBg = when (goal.aiPrediction) {
        "achieved" -> CardGreen
        "on_track" -> CardBlue
        "at_risk" -> Color(0xFFFFF3E0)
        "failed" -> CardRed
        else -> Color(0xFFF5F7FF)
    }
    val goalTypeIcon = when (goal.goalType) {
        "save" -> Icons.Default.Savings
        "limit_category" -> Icons.Default.Category
        "limit_spending" -> Icons.Default.MoneyOff
        "emergency_fund" -> Icons.Default.AccountBalance
        else -> Icons.Default.TrackChanges
    }

    Card(
        modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Box(
                    Modifier.size(44.dp).clip(CircleShape).background(CardBlue),
                    Alignment.Center
                ) {
                    Icon(goalTypeIcon, null, tint = PrimaryBlue, modifier = Modifier.size(22.dp))
                }
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text(goal.title, fontWeight = FontWeight.Bold, fontSize = 15.sp,
                        color = Color(0xFF0D1B4B))
                    Text(goal.goalType.replace("_", " ").replaceFirstChar { it.uppercase() } +
                            (goal.category?.let { " · $it" } ?: ""),
                        fontSize = 12.sp, color = Color(0xFF6B7DB3))
                }
                goal.aiPrediction?.let { pred ->
                    Surface(shape = RoundedCornerShape(8.dp), color = predictionBg) {
                        Text(
                            pred.replace("_", " "),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            color = predictionColor, fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            Spacer(Modifier.height(14.dp))

            // Progress
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("₹${goal.currentAmount.toLong()} / ₹${goal.targetAmount.toLong()}",
                    fontSize = 13.sp, color = Color(0xFF6B7DB3))
                Text("${goal.progressPercentage.toInt()}%",
                    fontWeight = FontWeight.Bold, fontSize = 13.sp,
                    color = predictionColor)
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(
                progress = { (goal.progressPercentage.toFloat() / 100f).coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                color = predictionColor,
                trackColor = Color(0xFFEEF1FB)
            )

            if (goal.deadline != null || goal.isAchieved) {
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (goal.isAchieved) {
                        Surface(shape = RoundedCornerShape(6.dp), color = CardGreen) {
                            Row(Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.CheckCircle, null, tint = AccentGreen,
                                    modifier = Modifier.size(12.dp))
                                Spacer(Modifier.width(4.dp))
                                Text("Achieved!", fontSize = 11.sp, color = AccentGreen,
                                    fontWeight = FontWeight.SemiBold)
                            }
                        }
                    }
                    goal.deadline?.let {
                        Surface(shape = RoundedCornerShape(6.dp), color = Color(0xFFF5F7FF)) {
                            Row(Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.CalendarToday, null, tint = Color(0xFF6B7DB3),
                                    modifier = Modifier.size(12.dp))
                                Spacer(Modifier.width(4.dp))
                                Text("Due: $it", fontSize = 11.sp, color = Color(0xFF6B7DB3))
                            }
                        }
                    }
                }
            }
        }
    }
}

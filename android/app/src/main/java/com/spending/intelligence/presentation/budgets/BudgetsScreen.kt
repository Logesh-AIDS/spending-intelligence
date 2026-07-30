package com.spending.intelligence.presentation.budgets

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.spending.intelligence.domain.model.Goal

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BudgetsScreen(
    onBack: () -> Unit,
    onNavigate: ((String) -> Unit)? = null,
    viewModel: BudgetsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Budget Goals") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, null) } }
            )
        }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
            state.goals.isEmpty() -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("No budget goals yet", fontWeight = FontWeight.SemiBold)
                    Text("Create goals in the web app to track them here",
                        fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
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
        "achieved" -> Color(0xFF10B981)
        "on_track" -> Color(0xFF3B82F6)
        "at_risk" -> Color(0xFFF59E0B)
        "failed" -> Color(0xFFEF4444)
        else -> Color.Gray
    }

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(goal.title, fontWeight = FontWeight.SemiBold)
                    Text(goal.goalType.replace("_", " ").replaceFirstChar { it.uppercase() },
                        fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                goal.aiPrediction?.let { pred ->
                    Surface(
                        shape = MaterialTheme.shapes.small,
                        color = predictionColor.copy(alpha = 0.15f)
                    ) {
                        Text(pred.replace("_", " "), modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            color = predictionColor, fontSize = 11.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }
            Spacer(Modifier.height(12.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("₹${goal.currentAmount.toLong()} / ₹${goal.targetAmount.toLong()}",
                    fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text("${goal.progressPercentage.toInt()}%", fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(
                progress = { (goal.progressPercentage.toFloat() / 100f).coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().height(6.dp),
                color = predictionColor
            )
            if (goal.deadline != null) {
                Spacer(Modifier.height(6.dp))
                Text("Due: ${goal.deadline}", fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

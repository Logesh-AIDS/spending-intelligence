package com.spending.intelligence.presentation.notifications

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Circle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.spending.intelligence.domain.model.Notification

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationsScreen(
    onBack: () -> Unit,
    viewModel: NotificationsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Notifications") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, null) } }
            )
        }
    ) { padding ->
        when {
            state.isLoading -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
            state.notifications.isEmpty() -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                Text("No notifications yet", color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            else -> LazyColumn(
                Modifier.fillMaxSize().padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(state.notifications, key = { it.id }) { note ->
                    NotificationCard(note, onRead = { viewModel.markRead(note.id) })
                }
            }
        }
    }
}

@Composable
private fun NotificationCard(notification: Notification, onRead: () -> Unit) {
    val priorityColor = when (notification.priority) {
        "high" -> Color(0xFFEF4444)
        "medium" -> Color(0xFFF59E0B)
        else -> Color(0xFF6B7280)
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (!notification.isRead)
                MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
            else MaterialTheme.colorScheme.surface
        ),
        onClick = onRead
    ) {
        Row(Modifier.padding(12.dp)) {
            if (!notification.isRead) {
                Icon(Icons.Default.Circle, null, modifier = Modifier.size(8.dp).padding(top = 6.dp),
                    tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(8.dp))
            }
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(notification.title, fontWeight = FontWeight.SemiBold, fontSize = 14.sp,
                        modifier = Modifier.weight(1f))
                    Surface(shape = MaterialTheme.shapes.extraSmall,
                        color = priorityColor.copy(alpha = 0.15f)) {
                        Text(notification.priority, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                            color = priorityColor, fontSize = 10.sp)
                    }
                }
                Spacer(Modifier.height(4.dp))
                Text(notification.message, fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                if (notification.recommendedAction.isNotBlank()) {
                    Spacer(Modifier.height(4.dp))
                    Text("→ ${notification.recommendedAction}", fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.primary)
                }
            }
        }
    }
}

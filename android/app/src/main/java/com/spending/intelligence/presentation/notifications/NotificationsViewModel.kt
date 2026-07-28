package com.spending.intelligence.presentation.notifications

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.repository.SpendingRepository
import com.spending.intelligence.domain.model.ApiResult
import com.spending.intelligence.domain.model.Notification
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class NotificationsUiState(
    val isLoading: Boolean = false,
    val notifications: List<Notification> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class NotificationsViewModel @Inject constructor(private val repository: SpendingRepository) : ViewModel() {

    private val _state = MutableStateFlow(NotificationsUiState(isLoading = true))
    val state: StateFlow<NotificationsUiState> = _state

    init { load() }

    private fun load() {
        viewModelScope.launch {
            when (val r = repository.getNotifications()) {
                is ApiResult.Success -> _state.value = NotificationsUiState(notifications = r.data)
                is ApiResult.Error -> _state.value = NotificationsUiState(error = r.message)
                else -> {}
            }
        }
    }

    fun markRead(id: Int) {
        viewModelScope.launch {
            repository.markNotificationRead(id)
            _state.update { s ->
                s.copy(notifications = s.notifications.map {
                    if (it.id == id) it.copy(isRead = true) else it
                })
            }
        }
    }
}

package com.spending.intelligence.presentation.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.local.TokenDataStore
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.repository.SpendingRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val userName: String? = null,
    val userEmail: String? = null,
    val smsPermissionGranted: Boolean = false,
    val pendingSmsCount: Int = 0
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val repository: SpendingRepository,
    private val tokenDataStore: TokenDataStore,
    private val pendingSmsDao: PendingSmsDao
) : ViewModel() {

    val state: StateFlow<SettingsUiState> = combine(
        tokenDataStore.userName,
        tokenDataStore.userEmail,
        pendingSmsDao.getPendingCount()
    ) { name, email, pendingCount ->
        SettingsUiState(
            userName = name,
            userEmail = email,
            smsPermissionGranted = true, // updated by MainActivity
            pendingSmsCount = pendingCount
        )
    }.stateIn(viewModelScope, SharingStarted.Lazily, SettingsUiState())

    fun logout() {
        viewModelScope.launch { repository.logout() }
    }

    fun setSmsPermissionStatus(granted: Boolean) {
        // Trigger recompose with updated permission state
    }
}

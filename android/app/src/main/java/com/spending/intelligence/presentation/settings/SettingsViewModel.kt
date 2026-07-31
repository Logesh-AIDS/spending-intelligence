package com.spending.intelligence.presentation.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
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
    application: Application,
    private val repository: SpendingRepository,
    private val tokenDataStore: TokenDataStore,
    private val pendingSmsDao: PendingSmsDao
) : AndroidViewModel(application) {

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
        viewModelScope.launch {
            repository.logout()
            // Clear the uploaded SMS IDs so fresh account starts clean
            getApplication<Application>().getSharedPreferences("sms_uploaded_ids", android.content.Context.MODE_PRIVATE)
                .edit().clear().apply()
        }
    }

    fun setSmsPermissionStatus(granted: Boolean) {
        // Trigger recompose with updated permission state
    }
}

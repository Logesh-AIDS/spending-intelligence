package com.spending.intelligence.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.repository.SpendingRepository
import com.spending.intelligence.domain.model.ApiResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val isSuccess: Boolean = false
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: SpendingRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            _uiState.value = AuthUiState(error = "Email and password are required")
            return
        }
        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            // repository.login() now sets TokenHolder immediately
            when (val result = repository.login(email.trim(), password)) {
                is ApiResult.Success -> _uiState.value = AuthUiState(isSuccess = true)
                is ApiResult.Error -> _uiState.value = AuthUiState(error = result.message)
                else -> {}
            }
        }
    }

    fun register(email: String, password: String, fullName: String) {
        if (email.isBlank() || password.isBlank() || fullName.isBlank()) {
            _uiState.value = AuthUiState(error = "All fields are required")
            return
        }
        viewModelScope.launch {
            _uiState.value = AuthUiState(isLoading = true)
            when (val result = repository.register(email.trim(), password, fullName.trim())) {
                is ApiResult.Success -> _uiState.value = AuthUiState(isSuccess = true)
                is ApiResult.Error -> _uiState.value = AuthUiState(error = result.message)
                else -> {}
            }
        }
    }

    fun clearError() { _uiState.value = _uiState.value.copy(error = null) }
}

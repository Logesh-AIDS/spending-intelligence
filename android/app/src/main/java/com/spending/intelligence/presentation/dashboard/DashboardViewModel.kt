package com.spending.intelligence.presentation.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.repository.SpendingRepository
import com.spending.intelligence.domain.model.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardUiState(
    val isLoading: Boolean = false,
    val summary: DashboardSummary? = null,
    val healthScore: HealthScore? = null,
    val pendingSmsCount: Int = 0,
    val error: String? = null
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: SpendingRepository
) : ViewModel() {

    private val _state = MutableStateFlow(DashboardUiState(isLoading = true))
    val state: StateFlow<DashboardUiState> = _state

    init { load() }

    fun load() {
        viewModelScope.launch {
            _state.value = DashboardUiState(isLoading = true)
            val summaryResult = repository.getDashboardSummary()
            val healthResult = repository.getHealthScore()
            _state.value = DashboardUiState(
                isLoading = false,
                summary = (summaryResult as? ApiResult.Success)?.data,
                healthScore = (healthResult as? ApiResult.Success)?.data,
                error = (summaryResult as? ApiResult.Error)?.message
            )
        }
    }
}

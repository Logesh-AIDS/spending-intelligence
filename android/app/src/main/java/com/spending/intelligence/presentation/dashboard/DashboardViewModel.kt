package com.spending.intelligence.presentation.dashboard

import android.util.Log
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
            try {
                Log.d("Dashboard", "Fetching dashboard summary...")
                val summaryResult = repository.getDashboardSummary()
                Log.d("Dashboard", "Summary result: $summaryResult")

                val healthScore = try {
                    val h = repository.getHealthScore()
                    Log.d("Dashboard", "Health result: $h")
                    (h as? ApiResult.Success)?.data
                } catch (e: Exception) {
                    Log.w("Dashboard", "Health score failed (non-fatal): ${e.message}")
                    null
                }

                when (summaryResult) {
                    is ApiResult.Success -> _state.value = DashboardUiState(
                        isLoading = false,
                        summary = summaryResult.data,
                        healthScore = healthScore
                    )
                    is ApiResult.Error -> {
                        Log.e("Dashboard", "Summary error: ${summaryResult.message}")
                        _state.value = DashboardUiState(
                            isLoading = false,
                            error = summaryResult.message
                        )
                    }
                    else -> _state.value = DashboardUiState(isLoading = false, error = "Unknown error")
                }
            } catch (e: Exception) {
                Log.e("Dashboard", "Unexpected crash: ${e::class.simpleName}: ${e.message}", e)
                _state.value = DashboardUiState(
                    isLoading = false,
                    error = "${e::class.simpleName}: ${e.message}"
                )
            }
        }
    }
}

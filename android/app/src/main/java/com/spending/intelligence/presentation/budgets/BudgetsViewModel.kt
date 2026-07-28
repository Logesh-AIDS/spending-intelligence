package com.spending.intelligence.presentation.budgets

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.repository.SpendingRepository
import com.spending.intelligence.domain.model.ApiResult
import com.spending.intelligence.domain.model.Goal
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class BudgetsUiState(
    val isLoading: Boolean = false,
    val goals: List<Goal> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class BudgetsViewModel @Inject constructor(private val repository: SpendingRepository) : ViewModel() {

    private val _state = MutableStateFlow(BudgetsUiState(isLoading = true))
    val state: StateFlow<BudgetsUiState> = _state

    init { load() }

    fun load() {
        viewModelScope.launch {
            _state.value = BudgetsUiState(isLoading = true)
            when (val result = repository.getGoals()) {
                is ApiResult.Success -> _state.value = BudgetsUiState(goals = result.data)
                is ApiResult.Error -> _state.value = BudgetsUiState(error = result.message)
                else -> {}
            }
        }
    }
}

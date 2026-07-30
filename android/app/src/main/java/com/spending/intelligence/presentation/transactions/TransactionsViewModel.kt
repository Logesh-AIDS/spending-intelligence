package com.spending.intelligence.presentation.transactions

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.repository.SpendingRepository
import com.spending.intelligence.domain.model.ApiResult
import com.spending.intelligence.domain.model.Transaction
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TransactionsUiState(
    val transactions: List<Transaction> = emptyList(),
    val isSyncing: Boolean = false,
    val error: String? = null,
    val deleteSuccess: Boolean = false
)

@OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
@HiltViewModel
class TransactionsViewModel @Inject constructor(
    private val repository: SpendingRepository
) : ViewModel() {

    private val _search = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _search

    private val _error = MutableStateFlow<String?>(null)
    private val _isSyncing = MutableStateFlow(false)

    val transactions: StateFlow<List<Transaction>> = _search
        .debounce(300)
        .flatMapLatest { query ->
            if (query.isBlank()) repository.getLocalTransactions()
            else repository.searchLocalTransactions(query)
        }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    val uiState: StateFlow<TransactionsUiState> = combine(
        transactions, _isSyncing, _error
    ) { txns, syncing, err ->
        TransactionsUiState(txns, syncing, err)
    }.stateIn(viewModelScope, SharingStarted.Lazily, TransactionsUiState())

    init { sync() }

    fun setSearch(query: String) { _search.value = query }

    fun sync() {
        viewModelScope.launch {
            _isSyncing.value = true
            try {
                val result = repository.syncTransactions()
                if (result is ApiResult.Error) {
                    // Only show error if it's not a network issue during offline use
                    if (!result.message.contains("Network", ignoreCase = true)) {
                        _error.value = result.message
                    }
                }
            } catch (e: Exception) {
                // Silently ignore sync errors — local data still shows
            } finally {
                _isSyncing.value = false
            }
        }
    }

    fun delete(id: Int) {
        viewModelScope.launch {
            val result = repository.deleteTransaction(id)
            if (result is ApiResult.Error) _error.value = result.message
        }
    }

    fun clearError() { _error.value = null }
}

package com.spending.intelligence.presentation.analytics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.remote.api.SpendingApi
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CategoryData(val categories: List<CategoryItem>, val highestCategory: String?)
data class CategoryItem(val category: String, val totalSpent: Double, val percentage: Double)
data class BehaviourData(val averageSpending: Double, val medianSpending: Double, val maxSpending: Double,
                         val weekendSpending: Double, val mostActiveDay: String?, val frequencyPerDay: Double)
data class StatisticsData(val totalTransactions: Int, val totalDebitAmount: Double, val totalCreditAmount: Double,
                          val avgDebitAmount: Double, val highestDebit: Double?)

data class AnalyticsUiState(
    val isLoading: Boolean = false,
    val categoryData: CategoryData? = null,
    val behaviour: BehaviourData? = null,
    val statistics: StatisticsData? = null,
    val error: String? = null
)

@HiltViewModel
class AnalyticsViewModel @Inject constructor(private val api: SpendingApi) : ViewModel() {

    private val _state = MutableStateFlow(AnalyticsUiState(isLoading = true))
    val state: StateFlow<AnalyticsUiState> = _state

    init { load() }

    private fun load() {
        viewModelScope.launch {
            try {
                val catRes = api.getCategories()
                val behRes = api.getBehaviour()
                val statRes = api.getStatistics()

                val cat = if (catRes.isSuccessful) catRes.body()!!.let { body ->
                    CategoryData(
                        categories = body.categories.map { CategoryItem(it.category, it.totalSpent, it.percentage) },
                        highestCategory = body.highestSpendingCategory
                    )
                } else null

                val beh = if (behRes.isSuccessful) behRes.body()!!.let { b ->
                    BehaviourData(b.averageSpending, b.medianSpending, b.maxSpending,
                        b.weekendSpending, b.mostActiveDay, b.transactionFrequencyPerDay)
                } else null

                val stat = if (statRes.isSuccessful) statRes.body()!!.let { s ->
                    StatisticsData(s.totalTransactions, s.totalDebitAmount, s.totalCreditAmount,
                        s.averageDebitAmount, s.highestDebit)
                } else null

                _state.value = AnalyticsUiState(categoryData = cat, behaviour = beh, statistics = stat)
            } catch (e: Exception) {
                _state.value = AnalyticsUiState(error = "Network error: ${e.message}")
            }
        }
    }
}

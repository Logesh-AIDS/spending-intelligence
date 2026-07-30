package com.spending.intelligence.presentation.analytics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.spending.intelligence.data.remote.api.SpendingApi
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CategoryItem(val category: String, val totalSpent: Double, val percentage: Double)
data class CategoryData(val categories: List<CategoryItem>, val highestCategory: String?)
data class BehaviourData(
    val averageSpending: Double, val medianSpending: Double, val maxSpending: Double,
    val weekendSpending: Double, val weekdaySpending: Double,
    val mostActiveDay: String?, val frequencyPerDay: Double
)
data class StatisticsData(
    val totalTransactions: Int, val totalDebitAmount: Double, val totalCreditAmount: Double,
    val avgDebitAmount: Double, val highestDebit: Double?
)

data class AnalyticsUiState(
    val isLoading: Boolean = true,
    val categoryData: CategoryData? = null,
    val behaviour: BehaviourData? = null,
    val statistics: StatisticsData? = null,
    val error: String? = null
)

@HiltViewModel
class AnalyticsViewModel @Inject constructor(private val api: SpendingApi) : ViewModel() {

    private val _state = MutableStateFlow(AnalyticsUiState())
    val state: StateFlow<AnalyticsUiState> = _state

    init { load() }

    fun load() {
        viewModelScope.launch {
            _state.value = AnalyticsUiState(isLoading = true)

            // Fetch all 3 independently — partial failure still shows other data
            var cat: CategoryData? = null
            var beh: BehaviourData? = null
            var stat: StatisticsData? = null
            var errorMsg: String? = null

            try {
                val r = api.getCategories()
                if (r.isSuccessful && r.body() != null) {
                    val body = r.body()!!
                    cat = CategoryData(
                        categories = body.categories.map {
                            CategoryItem(it.category, it.totalSpent, it.percentage)
                        },
                        highestCategory = body.highestSpendingCategory
                    )
                }
            } catch (e: Exception) { errorMsg = e.message }

            try {
                val r = api.getBehaviour()
                if (r.isSuccessful && r.body() != null) {
                    val b = r.body()!!
                    beh = BehaviourData(
                        b.averageSpending, b.medianSpending, b.maxSpending,
                        b.weekendSpending, b.weekdaySpending,
                        b.mostActiveDay, b.transactionFrequencyPerDay
                    )
                }
            } catch (e: Exception) { /* continue */ }

            try {
                val r = api.getStatistics()
                if (r.isSuccessful && r.body() != null) {
                    val s = r.body()!!
                    stat = StatisticsData(
                        s.totalTransactions, s.totalDebitAmount, s.totalCreditAmount,
                        s.averageDebitAmount, s.highestDebit
                    )
                }
            } catch (e: Exception) { /* continue */ }

            _state.value = AnalyticsUiState(
                isLoading = false,
                categoryData = cat,
                behaviour = beh,
                statistics = stat,
                error = if (cat == null && beh == null && stat == null) errorMsg else null
            )
        }
    }
}

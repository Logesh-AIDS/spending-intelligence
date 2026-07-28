package com.spending.intelligence.data.remote.dto

import com.google.gson.annotations.SerializedName

data class CategoryItemDto(
    val category: String,
    @SerializedName("total_spent") val totalSpent: Double,
    @SerializedName("transaction_count") val transactionCount: Int,
    val percentage: Double
)

data class CategoryAnalyticsDto(
    @SerializedName("total_categories") val totalCategories: Int,
    @SerializedName("highest_spending_category") val highestSpendingCategory: String?,
    val categories: List<CategoryItemDto>
)

data class BehaviourDto(
    @SerializedName("average_spending") val averageSpending: Double,
    @SerializedName("median_spending") val medianSpending: Double,
    @SerializedName("max_spending") val maxSpending: Double,
    @SerializedName("min_spending") val minSpending: Double,
    @SerializedName("std_deviation") val stdDeviation: Double,
    @SerializedName("transaction_frequency_per_day") val transactionFrequencyPerDay: Double,
    @SerializedName("weekend_spending") val weekendSpending: Double,
    @SerializedName("weekday_spending") val weekdaySpending: Double,
    @SerializedName("weekend_vs_weekday_ratio") val weekendVsWeekdayRatio: Double,
    @SerializedName("most_active_day") val mostActiveDay: String?
)

data class StatisticsDto(
    @SerializedName("total_transactions") val totalTransactions: Int,
    @SerializedName("total_debit_transactions") val totalDebitTransactions: Int,
    @SerializedName("total_credit_transactions") val totalCreditTransactions: Int,
    @SerializedName("total_debit_amount") val totalDebitAmount: Double,
    @SerializedName("total_credit_amount") val totalCreditAmount: Double,
    @SerializedName("average_debit_amount") val averageDebitAmount: Double,
    @SerializedName("average_credit_amount") val averageCreditAmount: Double,
    @SerializedName("highest_debit") val highestDebit: Double?,
    @SerializedName("highest_credit") val highestCredit: Double?
)

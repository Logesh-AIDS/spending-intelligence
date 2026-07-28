package com.spending.intelligence.domain.model

data class User(
    val id: Int,
    val email: String,
    val fullName: String,
    val isActive: Boolean
)

data class Transaction(
    val id: Int,
    val bank: String,
    val accountNumber: String?,
    val transactionType: String,
    val amount: Double,
    val date: String,
    val merchant: String?,
    val upiReference: String?,
    val balance: Double?,
    val category: String,
    val createdAt: String
) {
    val isDebit get() = transactionType == "Debit"
    val isCredit get() = transactionType == "Credit"
    val displayAmount get() = if (isDebit) "-₹${amount.toLong()}" else "+₹${amount.toLong()}"
}

data class DashboardSummary(
    val currentBalance: Double?,
    val totalSpending: Double,
    val totalIncome: Double,
    val netCashFlow: Double,
    val savingsPercentage: Double,
    val todaySpending: Double,
    val thisWeekSpending: Double,
    val thisMonthSpending: Double,
    val totalTransactions: Int,
    val avgDailySpending: Double,
    val recentTransactions: List<Transaction>
)

data class HealthScore(
    val score: Double,
    val grade: String,
    val interpretation: String,
    val improvementTips: List<String>
)

data class Notification(
    val id: Int,
    val title: String,
    val message: String,
    val type: String,
    val priority: String,
    val aiExplanation: String,
    val recommendedAction: String,
    val isRead: Boolean,
    val createdAt: String
)

data class Goal(
    val id: Int,
    val title: String,
    val goalType: String,
    val targetAmount: Double,
    val currentAmount: Double,
    val category: String?,
    val deadline: String?,
    val isAchieved: Boolean,
    val progressPercentage: Double,
    val aiPrediction: String?
)

sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val code: Int = 0) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

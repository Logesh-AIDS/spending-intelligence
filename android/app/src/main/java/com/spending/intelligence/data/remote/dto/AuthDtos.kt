package com.spending.intelligence.data.remote.dto

import com.google.gson.annotations.SerializedName

data class LoginRequest(val email: String, val password: String)

data class RegisterRequest(
    val email: String,
    val password: String,
    @SerializedName("full_name") val fullName: String
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String
)

data class UserDto(
    val id: Int,
    val email: String,
    @SerializedName("full_name") val fullName: String,
    @SerializedName("is_active") val isActive: Boolean
)

data class SmsRequest(@SerializedName("raw_sms") val rawSms: String)

// Full transaction from /transactions/ endpoint — all fields present
data class TransactionDto(
    val id: Int = 0,
    val bank: String = "",
    @SerializedName("account_number") val accountNumber: String? = null,
    @SerializedName("transaction_type") val transactionType: String = "",
    val amount: Double = 0.0,
    val date: String = "",
    val merchant: String? = null,
    @SerializedName("upi_reference") val upiReference: String? = null,
    val balance: Double? = null,
    val category: String = "Others",
    @SerializedName("created_at") val createdAt: String? = null
)

// Simplified transaction from dashboard /summary — fewer fields
data class RecentTransactionDto(
    val id: Int = 0,
    val bank: String = "",
    @SerializedName("transaction_type") val transactionType: String = "",
    val amount: Double = 0.0,
    val date: String = "",
    val merchant: String? = null,
    val category: String = "Others",
    // Optional fields that may or may not be present
    @SerializedName("account_number") val accountNumber: String? = null,
    @SerializedName("upi_reference") val upiReference: String? = null,
    val balance: Double? = null,
    @SerializedName("created_at") val createdAt: String? = null
)

data class PaginatedTransactionsDto(
    @SerializedName("total_records") val totalRecords: Int,
    @SerializedName("current_page") val currentPage: Int,
    @SerializedName("total_pages") val totalPages: Int,
    @SerializedName("has_next") val hasNext: Boolean,
    @SerializedName("has_previous") val hasPrevious: Boolean,
    val transactions: List<TransactionDto>
)

// Every field has a default value so Gson NEVER throws on missing/null fields
data class DashboardSummaryDto(
    @SerializedName("current_balance") val currentBalance: Double? = null,
    @SerializedName("total_spending") val totalSpending: Double = 0.0,
    @SerializedName("total_income") val totalIncome: Double = 0.0,
    @SerializedName("net_cash_flow") val netCashFlow: Double = 0.0,
    @SerializedName("savings_percentage") val savingsPercentage: Double = 0.0,
    @SerializedName("today_spending") val todaySpending: Double = 0.0,
    @SerializedName("this_week_spending") val thisWeekSpending: Double = 0.0,
    @SerializedName("this_month_spending") val thisMonthSpending: Double = 0.0,
    @SerializedName("this_year_spending") val thisYearSpending: Double = 0.0,
    @SerializedName("total_transactions") val totalTransactions: Int = 0,
    @SerializedName("debit_count") val debitCount: Int = 0,
    @SerializedName("credit_count") val creditCount: Int = 0,
    @SerializedName("highest_expense") val highestExpense: Double? = null,
    @SerializedName("highest_income") val highestIncome: Double? = null,
    @SerializedName("average_transaction") val averageTransaction: Double? = null,
    @SerializedName("average_daily_spending") val avgDailySpending: Double = 0.0,
    // Use RecentTransactionDto which handles both full and minimal response shapes
    @SerializedName("recent_transactions") val recentTransactions: List<RecentTransactionDto> = emptyList()
)

data class HealthScoreDto(
    val score: Double = 0.0,
    val grade: String = "C",
    val interpretation: String = "",
    @SerializedName("improvement_tips") val improvementTips: List<String> = emptyList()
)

data class NotificationDto(
    val id: Int = 0,
    val title: String = "",
    val message: String = "",
    @SerializedName("notification_type") val type: String = "",
    val priority: String = "low",
    @SerializedName("ai_explanation") val aiExplanation: String = "",
    @SerializedName("recommended_action") val recommendedAction: String = "",
    @SerializedName("is_read") val isRead: Boolean = false,
    @SerializedName("created_at") val createdAt: String = ""
)

data class GoalDto(
    val id: Int = 0,
    val title: String = "",
    @SerializedName("goal_type") val goalType: String = "",
    @SerializedName("target_amount") val targetAmount: Double = 0.0,
    @SerializedName("current_amount") val currentAmount: Double = 0.0,
    val category: String? = null,
    val deadline: String? = null,
    @SerializedName("is_achieved") val isAchieved: Boolean = false,
    @SerializedName("progress_percentage") val progressPercentage: Double = 0.0,
    @SerializedName("ai_prediction") val aiPrediction: String? = null
)

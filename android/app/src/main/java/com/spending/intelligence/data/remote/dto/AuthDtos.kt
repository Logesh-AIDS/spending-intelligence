package com.spending.intelligence.data.remote.dto

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val email: String,
    val password: String
)

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

data class SmsRequest(
    @SerializedName("raw_sms") val rawSms: String
)

data class TransactionDto(
    val id: Int,
    val bank: String,
    @SerializedName("account_number") val accountNumber: String?,
    @SerializedName("transaction_type") val transactionType: String,
    val amount: Double,
    val date: String,
    val merchant: String?,
    @SerializedName("upi_reference") val upiReference: String?,
    val balance: Double?,
    val category: String,
    @SerializedName("created_at") val createdAt: String
)

data class PaginatedTransactionsDto(
    @SerializedName("total_records") val totalRecords: Int,
    @SerializedName("current_page") val currentPage: Int,
    @SerializedName("total_pages") val totalPages: Int,
    @SerializedName("has_next") val hasNext: Boolean,
    @SerializedName("has_previous") val hasPrevious: Boolean,
    val transactions: List<TransactionDto>
)

data class DashboardSummaryDto(
    @SerializedName("current_balance") val currentBalance: Double?,
    @SerializedName("total_spending") val totalSpending: Double,
    @SerializedName("total_income") val totalIncome: Double,
    @SerializedName("net_cash_flow") val netCashFlow: Double,
    @SerializedName("savings_percentage") val savingsPercentage: Double,
    @SerializedName("today_spending") val todaySpending: Double,
    @SerializedName("this_week_spending") val thisWeekSpending: Double,
    @SerializedName("this_month_spending") val thisMonthSpending: Double,
    @SerializedName("total_transactions") val totalTransactions: Int,
    @SerializedName("average_daily_spending") val avgDailySpending: Double,
    @SerializedName("recent_transactions") val recentTransactions: List<TransactionDto>
)

data class HealthScoreDto(
    val score: Double,
    val grade: String,
    val interpretation: String,
    @SerializedName("improvement_tips") val improvementTips: List<String>
)

data class NotificationDto(
    val id: Int,
    val title: String,
    val message: String,
    @SerializedName("notification_type") val type: String,
    val priority: String,
    @SerializedName("ai_explanation") val aiExplanation: String,
    @SerializedName("recommended_action") val recommendedAction: String,
    @SerializedName("is_read") val isRead: Boolean,
    @SerializedName("created_at") val createdAt: String
)

data class GoalDto(
    val id: Int,
    val title: String,
    @SerializedName("goal_type") val goalType: String,
    @SerializedName("target_amount") val targetAmount: Double,
    @SerializedName("current_amount") val currentAmount: Double,
    val category: String?,
    val deadline: String?,
    @SerializedName("is_achieved") val isAchieved: Boolean,
    @SerializedName("progress_percentage") val progressPercentage: Double,
    @SerializedName("ai_prediction") val aiPrediction: String?
)

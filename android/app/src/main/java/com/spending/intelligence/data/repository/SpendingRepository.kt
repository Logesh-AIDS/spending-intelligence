package com.spending.intelligence.data.repository

import com.spending.intelligence.data.local.TokenDataStore
import com.spending.intelligence.data.local.dao.TransactionDao
import com.spending.intelligence.data.local.entity.TransactionEntity
import com.spending.intelligence.data.remote.api.SpendingApi
import com.spending.intelligence.data.remote.dto.*
import com.spending.intelligence.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SpendingRepository @Inject constructor(
    private val api: SpendingApi,
    private val transactionDao: TransactionDao,
    private val tokenDataStore: TokenDataStore
) {

    // ── Auth ──────────────────────────────────────────────────────────────────

    suspend fun login(email: String, password: String): ApiResult<String> {
        return try {
            val response = api.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                val token = response.body()!!.accessToken
                tokenDataStore.saveToken(token)
                ApiResult.Success(token)
            } else {
                ApiResult.Error("Incorrect email or password", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Network error: ${e.message}")
        }
    }

    suspend fun register(email: String, password: String, fullName: String): ApiResult<User> {
        return try {
            val response = api.register(RegisterRequest(email, password, fullName))
            if (response.isSuccessful) {
                val user = response.body()!!
                ApiResult.Success(User(user.id, user.email, user.fullName, user.isActive))
            } else {
                ApiResult.Error("Registration failed", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Network error: ${e.message}")
        }
    }

    suspend fun getCurrentUser(): ApiResult<User> {
        return try {
            val response = api.getCurrentUser()
            if (response.isSuccessful) {
                val u = response.body()!!
                tokenDataStore.saveUserInfo(u.email, u.fullName)
                ApiResult.Success(User(u.id, u.email, u.fullName, u.isActive))
            } else {
                ApiResult.Error("Could not load profile", response.code())
            }
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    suspend fun logout() = tokenDataStore.clearAll()

    val savedToken: Flow<String?> = tokenDataStore.token

    // ── Dashboard ─────────────────────────────────────────────────────────────

    suspend fun getDashboardSummary(): ApiResult<DashboardSummary> {
        return try {
            val r = api.getDashboardSummary()
            if (r.isSuccessful) {
                val d = r.body()!!
                ApiResult.Success(
                    DashboardSummary(
                        currentBalance = d.currentBalance,
                        totalSpending = d.totalSpending,
                        totalIncome = d.totalIncome,
                        netCashFlow = d.netCashFlow,
                        savingsPercentage = d.savingsPercentage,
                        todaySpending = d.todaySpending,
                        thisWeekSpending = d.thisWeekSpending,
                        thisMonthSpending = d.thisMonthSpending,
                        totalTransactions = d.totalTransactions,
                        avgDailySpending = d.avgDailySpending,
                        recentTransactions = d.recentTransactions.map { it.toRecentDomain() }
                    )
                )            } else ApiResult.Error("Could not load dashboard", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    suspend fun getHealthScore(): ApiResult<HealthScore> {
        return try {
            val r = api.getHealthScore()
            if (r.isSuccessful) {
                val h = r.body()!!
                ApiResult.Success(HealthScore(h.score, h.grade, h.interpretation, h.improvementTips))
            } else ApiResult.Error("Could not load health score", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    // ── Transactions ──────────────────────────────────────────────────────────

    fun getLocalTransactions(): Flow<List<Transaction>> =
        transactionDao.getAllTransactions().map { list -> list.map { it.toDomain() } }

    fun searchLocalTransactions(query: String): Flow<List<Transaction>> =
        transactionDao.search(query).map { list -> list.map { it.toDomain() } }

    suspend fun syncTransactions(): ApiResult<Unit> {
        return try {
            val r = api.getTransactions(pageSize = 100)
            if (r.isSuccessful) {
                val txns = r.body()!!.transactions.map { it.toEntity() }
                transactionDao.upsertAll(txns)
                ApiResult.Success(Unit)
            } else ApiResult.Error("Sync failed", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    suspend fun deleteTransaction(id: Int): ApiResult<Unit> {
        return try {
            val r = api.deleteTransaction(id)
            if (r.isSuccessful) {
                transactionDao.deleteById(id)
                ApiResult.Success(Unit)
            } else ApiResult.Error("Delete failed", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    // ── Notifications ─────────────────────────────────────────────────────────

    suspend fun getNotifications(unreadOnly: Boolean = false): ApiResult<List<Notification>> {
        return try {
            val r = api.getNotifications(unreadOnly)
            if (r.isSuccessful) {
                ApiResult.Success(r.body()!!.map {
                    Notification(it.id, it.title, it.message, it.type, it.priority,
                        it.aiExplanation, it.recommendedAction, it.isRead, it.createdAt)
                })
            } else ApiResult.Error("Failed", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }

    suspend fun markNotificationRead(id: Int) {
        try { api.markNotificationRead(id) } catch (e: Exception) { }
    }

    // ── Goals ─────────────────────────────────────────────────────────────────

    suspend fun getGoals(): ApiResult<List<Goal>> {
        return try {
            val r = api.getGoals()
            if (r.isSuccessful) {
                ApiResult.Success(r.body()!!.map {
                    Goal(it.id, it.title, it.goalType, it.targetAmount, it.currentAmount,
                        it.category, it.deadline, it.isAchieved, it.progressPercentage, it.aiPrediction)
                })
            } else ApiResult.Error("Failed", r.code())
        } catch (e: Exception) {
            ApiResult.Error("Network error")
        }
    }
}

// ── Mappers ───────────────────────────────────────────────────────────────────

private fun TransactionDto.toDomain() = Transaction(
    id, bank, accountNumber, transactionType, amount, date,
    merchant, upiReference, balance, category, createdAt ?: ""
)

private fun TransactionDto.toEntity() = TransactionEntity(
    id, bank, accountNumber, transactionType, amount, date,
    merchant, upiReference, balance, category, createdAt ?: ""
)

private fun TransactionEntity.toDomain() = Transaction(
    id, bank, accountNumber, transactionType, amount, date,
    merchant, upiReference, balance, category, createdAt
)

// Maps the simplified dashboard recent_transactions shape (missing some fields)
private fun com.spending.intelligence.data.remote.dto.RecentTransactionDto.toRecentDomain() = Transaction(
    id = id,
    bank = bank,
    accountNumber = accountNumber,
    transactionType = transactionType,
    amount = amount,
    date = date,
    merchant = merchant,
    upiReference = upiReference,
    balance = balance,
    category = category,
    createdAt = createdAt ?: ""
)

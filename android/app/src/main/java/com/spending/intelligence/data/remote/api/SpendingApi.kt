package com.spending.intelligence.data.remote.api

import com.spending.intelligence.data.remote.dto.*
import retrofit2.Response
import retrofit2.http.*

interface SpendingApi {

    // ── Auth ──────────────────────────────────────────────────────────────────
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<UserDto>

    @GET("auth/me")
    suspend fun getCurrentUser(): Response<UserDto>

    // ── SMS ───────────────────────────────────────────────────────────────────
    @POST("sms/")
    suspend fun parseSms(@Body request: SmsRequest): Response<Any>

    // ── Transactions ──────────────────────────────────────────────────────────
    @GET("transactions/")
    suspend fun getTransactions(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20,
        @Query("transaction_type") type: String? = null,
        @Query("search") search: String? = null,
        @Query("sort_by") sortBy: String = "created_at",
        @Query("sort_order") sortOrder: String = "desc"
    ): Response<PaginatedTransactionsDto>

    @DELETE("transactions/{id}")
    suspend fun deleteTransaction(@Path("id") id: Int): Response<Any>

    // ── Dashboard ─────────────────────────────────────────────────────────────
    @GET("dashboard/summary")
    suspend fun getDashboardSummary(): Response<DashboardSummaryDto>

    // ── Health Score ──────────────────────────────────────────────────────────
    @GET("health-score")
    suspend fun getHealthScore(): Response<HealthScoreDto>

    // ── Notifications ─────────────────────────────────────────────────────────
    @GET("notifications")
    suspend fun getNotifications(@Query("unread_only") unreadOnly: Boolean = false): Response<List<NotificationDto>>

    @POST("notifications/{id}/read")
    suspend fun markNotificationRead(@Path("id") id: Int): Response<Any>

    // ── Goals ─────────────────────────────────────────────────────────────────
    @GET("goals")
    suspend fun getGoals(): Response<List<GoalDto>>
}

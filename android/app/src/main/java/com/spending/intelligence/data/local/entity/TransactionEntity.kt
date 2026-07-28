package com.spending.intelligence.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "transactions")
data class TransactionEntity(
    @PrimaryKey val id: Int,
    val bank: String,
    val accountNumber: String?,
    val transactionType: String,   // "Debit" or "Credit"
    val amount: Double,
    val date: String,              // DD/MM/YY
    val merchant: String?,
    val upiReference: String?,
    val balance: Double?,
    val category: String,
    val createdAt: String
)

// Pending SMS uploads — stored locally when offline, uploaded when online
@Entity(tableName = "pending_sms")
data class PendingSmsEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val rawSms: String,
    val receivedAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

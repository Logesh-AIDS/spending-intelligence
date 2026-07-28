package com.spending.intelligence.data.local.dao

import androidx.room.*
import com.spending.intelligence.data.local.entity.PendingSmsEntity
import com.spending.intelligence.data.local.entity.TransactionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TransactionDao {

    @Query("SELECT * FROM transactions ORDER BY createdAt DESC")
    fun getAllTransactions(): Flow<List<TransactionEntity>>

    @Query("SELECT * FROM transactions WHERE transactionType = :type ORDER BY createdAt DESC")
    fun getByType(type: String): Flow<List<TransactionEntity>>

    @Query("SELECT * FROM transactions WHERE merchant LIKE '%' || :query || '%' OR bank LIKE '%' || :query || '%' ORDER BY createdAt DESC")
    fun search(query: String): Flow<List<TransactionEntity>>

    @Upsert
    suspend fun upsertAll(transactions: List<TransactionEntity>)

    @Query("DELETE FROM transactions WHERE id = :id")
    suspend fun deleteById(id: Int)

    @Query("DELETE FROM transactions")
    suspend fun deleteAll()
}

@Dao
interface PendingSmsDao {

    @Insert
    suspend fun insert(sms: PendingSmsEntity): Long

    @Query("SELECT * FROM pending_sms ORDER BY receivedAt ASC LIMIT 50")
    suspend fun getPending(): List<PendingSmsEntity>

    @Query("DELETE FROM pending_sms WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("UPDATE pending_sms SET retryCount = retryCount + 1 WHERE id = :id")
    suspend fun incrementRetry(id: Long)

    @Query("DELETE FROM pending_sms WHERE retryCount >= 5")
    suspend fun deleteExhausted()

    @Query("SELECT COUNT(*) FROM pending_sms")
    fun getPendingCount(): Flow<Int>
}

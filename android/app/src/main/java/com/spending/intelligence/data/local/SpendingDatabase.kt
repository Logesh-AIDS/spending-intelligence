package com.spending.intelligence.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.local.dao.TransactionDao
import com.spending.intelligence.data.local.entity.PendingSmsEntity
import com.spending.intelligence.data.local.entity.TransactionEntity

@Database(
    entities = [TransactionEntity::class, PendingSmsEntity::class],
    version = 1,
    exportSchema = false
)
abstract class SpendingDatabase : RoomDatabase() {
    abstract fun transactionDao(): TransactionDao
    abstract fun pendingSmsDao(): PendingSmsDao
}

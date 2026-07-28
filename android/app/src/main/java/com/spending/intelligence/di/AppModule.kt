package com.spending.intelligence.di

import android.content.Context
import androidx.room.Room
import com.spending.intelligence.BuildConfig
import com.spending.intelligence.data.local.SpendingDatabase
import com.spending.intelligence.data.local.TokenDataStore
import com.spending.intelligence.data.local.dao.PendingSmsDao
import com.spending.intelligence.data.local.dao.TransactionDao
import com.spending.intelligence.data.remote.api.SpendingApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext ctx: Context): SpendingDatabase =
        Room.databaseBuilder(ctx, SpendingDatabase::class.java, "spending.db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides fun provideTransactionDao(db: SpendingDatabase): TransactionDao = db.transactionDao()
    @Provides fun providePendingSmsDao(db: SpendingDatabase): PendingSmsDao = db.pendingSmsDao()

    @Provides
    @Singleton
    fun provideOkHttpClient(tokenDataStore: TokenDataStore): OkHttpClient {
        val authInterceptor = Interceptor { chain ->
            // Read token synchronously (DataStore provides it from disk cache)
            val token = runBlocking { tokenDataStore.token.first() }
            val request = if (token != null) {
                chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            } else {
                chain.request()
            }
            chain.proceed(request)
        }

        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .apply {
                if (BuildConfig.DEBUG) {
                    addInterceptor(HttpLoggingInterceptor().apply {
                        level = HttpLoggingInterceptor.Level.BODY
                    })
                }
            }
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideApi(retrofit: Retrofit): SpendingApi = retrofit.create(SpendingApi::class.java)
}

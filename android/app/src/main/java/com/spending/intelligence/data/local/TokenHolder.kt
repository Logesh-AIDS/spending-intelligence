package com.spending.intelligence.data.local

import javax.inject.Inject
import javax.inject.Singleton

/**
 * In-memory token holder.
 * OkHttp interceptor reads from here synchronously — no coroutines, no deadlock.
 * Token is loaded into here at app startup from DataStore.
 */
@Singleton
class TokenHolder @Inject constructor() {
    @Volatile
    var token: String? = null
}

# Retrofit + OkHttp
-dontwarn okhttp3.**
-keepclassmembers class * { @retrofit2.http.* <methods>; }

# Gson serialization
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }
-keep class com.spending.intelligence.data.remote.dto.** { *; }

# Hilt
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# WorkManager
-keep class * extends androidx.work.Worker
-keep class * extends androidx.work.CoroutineWorker

# Keep data classes used with Gson
-keepclassmembers class * { public <init>(...); }

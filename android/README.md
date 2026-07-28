# SpendControl Android App

Automatic bank SMS detection + AI-powered spending intelligence on Android.

## Architecture

```
MVVM + Clean Architecture
├── presentation/   ← Jetpack Compose UI + ViewModels
├── domain/         ← Models, business rules
├── data/
│   ├── remote/     ← Retrofit API + DTOs
│   └── local/      ← Room DB (offline cache + SMS queue)
├── sms/            ← SMS receiver + smart filter
├── worker/         ← WorkManager background sync
├── di/             ← Hilt dependency injection
└── navigation/     ← Navigation Compose graph
```

## Key Features

| Feature | Implementation |
|---|---|
| Auto SMS detection | BroadcastReceiver + SmsFilter |
| Offline queue | Room `pending_sms` table |
| Background sync | WorkManager (15-min periodic + immediate on SMS) |
| Auth | JWT stored in DataStore, injected via OkHttp interceptor |
| Local cache | Room mirrors backend transactions for offline viewing |
| Retry logic | 5 retries per SMS, exponential backoff |

## Setup

1. Open `android/` in Android Studio
2. Set `BASE_URL` in `app/build.gradle.kts` debug block to your backend IP  
   (emulator: `http://10.0.2.2:8000/api/v1/`, physical device: `http://192.168.x.x:8000/api/v1/`)
3. Run on device or emulator (API 26+)

## SMS Flow

```
Bank SMS arrives
      ↓
SmsReceiver.onReceive()
      ↓
SmsFilter.filter() — OTP/promo/unsupported filtered out
      ↓
PendingSmsDao.insert() — saved to local queue
      ↓
SmsSyncWorker triggered
      ↓
POST /api/v1/sms/ — backend parses + saves transaction
      ↓
Transaction appears in app on next sync
```

## Adding a New Bank

Edit `SmsFilter.kt`:
1. Add sender IDs to `SUPPORTED_SENDERS`
2. The backend parser handles the actual extraction — add a parser in `backend/app/parsers/`

## Building for Release

```bash
./gradlew assembleRelease
```

Set `BASE_URL` in release build config to your production API URL.

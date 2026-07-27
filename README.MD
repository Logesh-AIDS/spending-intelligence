# AI Spending Intelligence

An intelligent personal finance assistant that parses bank SMS messages, tracks transactions, generates AI-powered insights, and predicts financial behaviour.

---

## Project Structure

```
Spending-Intelligence/
├── backend/          ← FastAPI REST API + ML services
├── frontend/         ← Next.js 15 web application
├── ml/               ← Machine Learning pipeline
├── automation/       ← Background jobs, scheduler, notifications
└── spending.db       ← SQLite database (auto-created on first run)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| Database | SQLite + SQLAlchemy ORM |
| Authentication | JWT (python-jose) + bcrypt |
| Frontend | Next.js 15, React 19, TypeScript |
| Styling | Tailwind CSS v4 + shadcn/ui |
| State Management | Zustand + TanStack Query |
| Charts | Recharts |
| ML | scikit-learn, XGBoost, pandas |
| Scheduler | APScheduler |

---

## Quick Start

### Prerequisites
- Python 3.11+ (Anaconda recommended)
- Node.js 20+
- pnpm (`npm install -g pnpm`)

### 1. Clone the repository
```bash
git clone <repo-url>
cd Spending-Intelligence
```

### 2. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

The API starts at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 3. Start the Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

The app starts at `http://localhost:3000`

### 4. Train the ML Models (first time only)

```bash
cd Spending-Intelligence   # project root
python -m ml.pipelines.train_all
```

---

## Environment Variables

### Backend
No `.env` file required for local development. All defaults work out of the box.

For production, set:
```
SECRET_KEY=your-secret-key-here        # JWT signing key
DATABASE_URL=sqlite:///spending.db     # or PostgreSQL URL
```

### Frontend
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Backend API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login, returns JWT |
| GET  | `/api/v1/auth/me` | Current user profile |

### SMS
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/sms/` | Parse bank SMS → save transaction |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| GET  | `/api/v1/transactions/` | List with filter/sort/pagination |
| POST | `/api/v1/transactions/` | Create manually |
| GET  | `/api/v1/transactions/{id}` | Get single |
| PUT  | `/api/v1/transactions/{id}` | Update |
| DELETE | `/api/v1/transactions/{id}` | Delete |

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/dashboard/summary` | Full financial snapshot |
| GET | `/api/v1/dashboard/today` | Today's activity |
| GET | `/api/v1/dashboard/weekly` | This week breakdown |
| GET | `/api/v1/dashboard/monthly` | Monthly dashboard |
| GET | `/api/v1/dashboard/balance-timeline` | Balance history |
| GET | `/api/v1/dashboard/spending-trend` | Spending trend chart |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/merchants` | Merchant breakdown |
| GET | `/api/v1/analytics/categories` | Category breakdown |
| GET | `/api/v1/analytics/income-vs-expense` | Period comparison |
| GET | `/api/v1/analytics/behaviour` | Spending behaviour |
| GET | `/api/v1/analytics/statistics` | Financial stats |
| GET | `/api/v1/analytics/search` | Advanced search |
| GET | `/api/v1/analytics/report` | Period report |

### ML APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ml/predict-spending` | Predict next transaction |
| POST | `/api/v1/ml/predict-cash-exhaustion` | Days until low balance |
| POST | `/api/v1/ml/detect-anomaly` | Anomaly detection |
| POST | `/api/v1/ml/recommendations` | AI recommendations |
| GET  | `/api/v1/ml/model-info` | Model versions & metrics |

### Automation
| Method | Endpoint | Description |
|---|---|---|
| GET  | `/api/v1/notifications` | User notifications |
| POST | `/api/v1/notifications/generate` | Trigger notifications |
| POST | `/api/v1/notifications/{id}/read` | Mark read |
| POST | `/api/v1/goals` | Create budget goal |
| GET  | `/api/v1/goals` | List goals |
| GET  | `/api/v1/goals/{id}/evaluate` | AI goal evaluation |
| DELETE | `/api/v1/goals/{id}` | Remove goal |
| GET  | `/api/v1/health-score` | Financial health score |
| GET  | `/api/v1/insights` | AI insights |
| POST | `/api/v1/insights/generate` | Generate insights |
| GET  | `/api/v1/admin/job-logs` | Background job history |
| POST | `/api/v1/admin/run-daily-analysis` | Manual daily job |
| POST | `/api/v1/admin/retrain-models` | Retrain ML models |
| GET  | `/api/v1/admin/scheduler-status` | Cron job status |

---

## Database Schema

```
users                    transactions
─────────────────        ──────────────────────────
id (PK)                  id (PK)
email (unique)           user_id (FK → users.id)
full_name                bank
hashed_password          account_number
is_active                transaction_type (Debit/Credit)
created_at               amount
                         date (DD/MM/YY)
                         merchant
                         upi_reference
                         balance
                         category
                         created_at

goals                    notifications
─────────────────        ──────────────────────────
id (PK)                  id (PK)
user_id (FK)             user_id (FK)
title                    title
goal_type                message
target_amount            notification_type
current_amount           priority
category                 is_read
deadline                 created_at
is_achieved
progress_percentage
ai_prediction
```

---

## ML Pipeline

The ML pipeline lives in `ml/` and is separate from the API:

```bash
# Run full data pipeline + train all models
python -m ml.pipelines.train_all

# Run data pipeline only (no training)
python -m ml.pipelines.run_pipeline

# Run for a specific user
python -m ml.pipelines.run_pipeline --user_id 1

# Skip EDA charts
python -m ml.pipelines.run_pipeline --skip_eda
```

**Models trained:**
- `spending_predictor` — GradientBoosting regression (RMSE ₹161, R²=0.98)
- `anomaly_detector` — Isolation Forest
- `cash_exhaustion_regressor` — GradientBoosting regression
- `user_segmentation` — K-Means clustering

---

## Supported Banks

| Bank | Status |
|---|---|
| Canara Bank | ✅ Full support |
| HDFC, SBI, ICICI, etc. | 🔜 Parser can be added in `backend/app/parsers/` |

To add a new bank:
1. Create `backend/app/parsers/hdfc_parser.py`
2. Register it in `backend/app/parsers/sms_parser.py`

---

## Background Scheduler

The scheduler runs automatically when the backend starts:
- **Daily 8:00 AM IST** — health scores, insights, notifications for all users
- **Every Sunday 2:00 AM** — ML model retraining

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Production Deployment

See [docs/deployment.md](docs/deployment.md) for deployment instructions.

Key checklist before deploying:
- [ ] Set `SECRET_KEY` environment variable
- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Set `NEXT_PUBLIC_API_URL` to production API URL
- [ ] Run `pnpm build` and verify clean build
- [ ] Train ML models on production data
- [ ] Configure CORS origins for production domain

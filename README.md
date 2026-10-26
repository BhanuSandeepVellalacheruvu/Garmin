# 🏃 Garmin AI Performance Lab

A complete, production-minded personal endurance analytics dashboard and open-weight AI training coach powered by your Garmin Connect data.

---

## ⚡ Highlights

- **Official Garmin Connect Personal API**: Direct, self-serve Bearer token exchange from your personal API key (`POST /personalapitoken-service/.../token`).
- **Local Open-Weight AI Coach**: Grounded natural-language training consultation powered by Ollama (`llama3.2`, `mistral`, `qwen2.5`) with real-time SSE streaming. Never invents stats; all calculations are executed deterministically in Python.
- **Biomechanical & Endurance Analytics**: 12-week volume progression, pace distributions, personal records (1K, 5K, 10K, Half, Marathon), acute:chronic workload ratio (ACWR), and pace-to-heart-rate aerobic efficiency.
- **Autonomic Recovery & Vitals**: Resting HR baseline, overnight HRV, sleep staging scores, Body Battery charge, and all-day physiological stress.
- **Zero-Setup Demo Mode**: Instantly testable out of the box with deterministic synthetic data (`GARMIN_PROVIDER=mock`, `LLM_PROVIDER=mock`).
- **One-Command Docker Deployment**: Ready to launch via `docker compose up --build`.

---

## 🏗️ Repository Architecture

```
garmin-ai-performance-lab/
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI Coach system prompt, context builder, tools, rules engine
│   │   ├── analytics/               # Deterministic running, health, and ACWR calculators
│   │   ├── api/v1/                  # FastAPI REST routers (activities, health, analytics, ai, etc.)
│   │   ├── core/                    # Settings, DB session, logging, Fernet token encryption
│   │   ├── models/                  # SQLAlchemy 2.0 async models (PostgreSQL)
│   │   ├── providers/
│   │   │   ├── garmin/              # GarminPersonalApiProvider, MockGarminProvider, normalizers
│   │   │   └── llm/                 # OpenAI-compatible / Ollama adapter & mock provider
│   │   ├── services/                # Idempotent Garmin sync & transaction orchestration
│   │   └── tasks/                   # APScheduler periodic incremental sync
│   ├── migrations/                  # Alembic database migrations
│   ├── tests/                       # Pytest test suite (11 unit & integration tests)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                        # Next.js 14 (App Router) + TypeScript + Tailwind + Recharts
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/           # Page A: Overview & Daily Vitals
│   │   │   ├── running/             # Page B: Running Analytics & Pacing
│   │   │   ├── health/              # Page C: Recovery & HRV
│   │   │   ├── calendar/            # Page D: Training Calendar & Race Goals
│   │   │   ├── activities/          # Page E: Activity Explorer & Detail splits
│   │   │   ├── coach/               # Page F: AI Coach Chat with SSE streaming
│   │   │   └── settings/            # Settings & Integrations
│   │   ├── components/              # Layout, charts, cards, banners
│   │   └── lib/                     # API client, types, formatters
│   └── Dockerfile
├── scripts/
│   ├── start.sh                     # Automated startup & healthcheck script
│   ├── seed_demo.sh                 # Demo data ingestion helper
│   └── reset.sh                     # Environment reset helper
├── docker-compose.yml               # Multi-service composition (Postgres 16, Backend, Frontend)
├── .env.example                     # Environment template
└── SECURITY.md                      # Security, secrets management, and privacy policy
```

---

## 🚀 Quick Start (One Command)

### 1. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```

*(By default, `.env.example` is configured for **Demo Mode** (`GARMIN_PROVIDER=mock`, `LLM_PROVIDER=mock`), allowing you to view and explore all pages immediately without any API keys or Ollama installation).*

### 2. Start the Application
Run the startup script:
```bash
./scripts/start.sh
```
Or directly with Docker Compose:
```bash
docker compose up --build -d
```

### 3. Open the Dashboard
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🔑 Obtaining Your Official Garmin Personal API Key

1. Log into your account on **Garmin Connect Web** ([https://connect.garmin.com](https://connect.garmin.com)).
2. In the left navigation menu, click **Settings** (gear icon) → **Account Information**.
3. Under the **API** section, select **Personal API Keys**.
4. Generate a new key and copy the key string.
5. In your `.env` file, configure:
   ```bash
   GARMIN_PROVIDER=official
   GARMIN_PERSONAL_API_KEY=your_copied_api_key
   ```
6. Restart or trigger a sync from the dashboard.

### Token Lifecycle & Authentication
- The backend automatically sends an authenticated request to `POST /personalapitoken-service/personal-api/personal-api-key/token` with header `Authorization: ApiKey <KEY>`.
- Garmin issues a Bearer token valid for **24 hours**.
- There are no refresh tokens; our backend caches the Bearer token securely in memory and re-exchanges the key 5 minutes prior to expiration.
- Raw API keys and authorization headers are never logged.

---

## 🧠 Setting Up Local Open-Weight LLM (Ollama)

For 100% private and offline AI coaching without sending your personal fitness data to third-party APIs:

1. **Install Ollama**:
   Download from [ollama.com](https://ollama.com) (macOS / Linux / Windows).

2. **Pull a Model**:
   ```bash
   ollama pull llama3.2
   ```
   *(Or `ollama pull mistral` / `ollama pull qwen2.5:7b`)*

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Update `.env`**:
   ```bash
   LLM_PROVIDER=ollama
   # When running backend in Docker on Mac/Windows:
   LLM_BASE_URL=http://host.docker.internal:11434/v1
   # When running backend natively:
   # LLM_BASE_URL=http://localhost:11434/v1
   LLM_MODEL=llama3.2
   ```

---

## 🧪 Running Automated Tests

To run the backend test suite:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```
All 11 unit and integration tests will verify:
- Analytical pace calculations and unit conversions
- Acute:chronic workload ratios (ACWR) and session classification
- Garmin API normalizer error tolerance
- Mock provider determinism
- API endpoints (health, status, activity search, AI recommendations)

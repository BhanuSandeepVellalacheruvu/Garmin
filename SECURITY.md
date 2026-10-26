# 🔒 Security and Privacy Policy

Garmin fitness and biometric data (heart rate, sleep staging, GPS locations, and body battery) constitute sensitive personal health information. The **Garmin AI Performance Lab** is designed from the ground up with defensive security principles.

---

## 1. Credentials and Secrets Protection

- **No Plaintext Tokens**: When access tokens are persisted to PostgreSQL in `ProviderCredential`, they are encrypted using Fernet symmetric encryption with a key dynamically derived from `APP_SECRET_KEY` using SHA-256.
- **Log Sanitization**: The application explicitly suppresses and redacts `Authorization` headers, `ApiKey` parameters, and Bearer tokens from all application and debug logs.
- **Environment Isolation**: All configuration is loaded through `pydantic-settings` via server-side environment variables. No client-side `NEXT_PUBLIC_*` secrets are used for Garmin or LLM credentials.
- **Strict `.gitignore`**: `.env`, `.env.*`, token caches, and SQLite/PostgreSQL dumps are excluded from version control.

---

## 2. LLM Data Privacy

- **Local-First Architecture**: By default, inference is routed to an on-device open-weight model hosted locally via Ollama. No health or workout telemetry leaves your local network.
- **Bounded Retrieval**: The LLM is never given direct access to raw database sockets or write permissions. It receives pre-aggregated, read-only summaries prepared by deterministic Python services.
- **Prompt Sanitization**: PII such as email addresses, user IDs, and auth credentials are excluded from the LLM system context.

---

## 3. Data Retention and Deletion

- You have full ownership of your data stored in PostgreSQL.
- To purge all stored activities, sleep records, and metrics:
  ```bash
  docker compose down -v
  ```
  This immediately destroys the PostgreSQL named volume `postgres_data`.

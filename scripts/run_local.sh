#!/usr/bin/env bash
# ============================================================
# Garmin AI Performance Lab — Local One-Command Runner
# Starts both FastAPI Backend and Next.js Frontend
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🏃 Starting Garmin AI Performance Lab..."

# Ensure .env exists
if [ ! -f ".env" ]; then
  cp .env.example .env
fi

# Trap Ctrl+C to kill both background processes
trap 'kill $(jobs -p) 2>/dev/null; echo ""; echo "🛑 Stopped Garmin AI Lab."; exit' SIGINT SIGTERM EXIT

# 1. Start Backend
echo "📡 Launching Backend API on http://localhost:8000..."
cd "$PROJECT_ROOT/backend"
if [ -f ".venv/bin/uvicorn" ]; then
  .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
else
  uvicorn app.main:app --host 0.0.0.0 --port 8000 &
fi
BACKEND_PID=$!

# 2. Wait for backend health
sleep 2

# 3. Start Frontend
echo "🌐 Launching Frontend Dashboard on http://localhost:3000..."
cd "$PROJECT_ROOT/frontend"
/opt/homebrew/opt/node@22/bin/npm run start &
FRONTEND_PID=$!

echo ""
echo "════════════════════════════════════════════════════════"
echo "  ✅ Garmin AI Performance Lab is LIVE!"
echo "════════════════════════════════════════════════════════"
echo "  🌐 Dashboard:   http://localhost:3000"
echo "  📡 API Docs:    http://localhost:8000/docs"
echo "  ⚡ Demo Mode:   Active (Synthetic Garmin data)"
echo "════════════════════════════════════════════════════════"
echo "  Press Ctrl+C to stop both servers."
echo ""

wait

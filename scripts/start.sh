#!/usr/bin/env bash
# Garmin AI Performance Lab — One-command startup
set -e

echo "🚀 Starting Garmin AI Performance Lab..."

if [ ! -f ".env" ]; then
  echo "❌ .env not found. Run: cp .env.example .env  then edit with your config."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker Desktop first."
  exit 1
fi

docker compose up --build -d

echo "⏳ Waiting for services to be healthy..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "✅ Backend healthy"
    break
  fi
  echo "   Attempt $i/30 — waiting 5s..."
  sleep 5
done

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ Garmin AI Performance Lab is running!"
echo "═══════════════════════════════════════════"
echo "  🌐 Dashboard:  http://localhost:3000"
echo "  📡 API:        http://localhost:8000"
echo "  📚 API Docs:   http://localhost:8000/docs"
echo "═══════════════════════════════════════════"
grep -q "GARMIN_PROVIDER=mock" .env && echo "  ⚡ DEMO MODE active (synthetic data)"
grep -q "LLM_PROVIDER=mock"    .env && echo "  🤖 AI MOCK MODE (no LLM needed)"
echo ""

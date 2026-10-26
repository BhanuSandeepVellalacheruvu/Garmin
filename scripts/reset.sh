#!/usr/bin/env bash
# Reset persistent volumes and restart
set -e

echo "⚠️  WARNING: This will delete all persistent database records. Press Ctrl+C within 5s to cancel."
sleep 5

docker compose down -v
docker compose up --build -d

echo "✅ Environment reset complete."

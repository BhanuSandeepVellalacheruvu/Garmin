#!/usr/bin/env bash
# Seed demo data via the backend API
set -e

echo "🌱 Seeding demo data into Garmin AI Performance Lab..."
curl -s -X POST http://localhost:8000/api/v1/garmin/sync/full \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2024-01-01", "end_date": "2024-12-31"}' | grep -o '"records_synced":[0-9]*' || echo "Completed."

echo "✅ Demo data seeded successfully."

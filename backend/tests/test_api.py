"""Integration tests for FastAPI endpoints."""
import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_garmin_status(client):
    res = await client.get("/api/v1/garmin/status")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "capabilities" in data


@pytest.mark.asyncio
async def test_activities_list(client):
    res = await client.get("/api/v1/activities")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_ai_recommendations(client):
    res = await client.get("/api/v1/ai/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]
    assert "action" in data[0]


@pytest.mark.asyncio
async def test_analytics_running_full_suite(client):
    res = await client.get("/api/v1/analytics/running/full-suite")
    assert res.status_code == 200
    data = res.json()
    assert "activities" in data
    assert "weekly_volume" in data
    assert "race_predictions" in data
    assert "vo2_max_estimate" in data
    assert "provenance" in data
    # Enforce data integrity: Unavailable metrics must be explicitly labeled
    assert data["provenance"]["ground_contact_time"]["status"] == "unavailable"
    assert data["provenance"]["vertical_oscillation"]["status"] == "unavailable"
    assert data["provenance"]["running_power"]["status"] == "unavailable"


@pytest.mark.asyncio
async def test_analytics_health_full_suite(client):
    res = await client.get("/api/v1/analytics/health/full-suite")
    assert res.status_code == 200
    data = res.json()
    assert "daily_records" in data
    assert "sleep_records" in data
    assert "provenance" in data
    assert "steps" in data["provenance"]
    assert "resting_heart_rate" in data["provenance"]


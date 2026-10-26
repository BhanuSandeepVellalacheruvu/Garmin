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

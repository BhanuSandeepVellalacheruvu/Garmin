"""Integration tests for Garmin Connect+ features."""
import pytest


@pytest.mark.asyncio
async def test_root_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_offers_perks(client):
    res = await client.get("/api/v1/offers")
    assert res.status_code == 200
    data = res.json()
    assert data["tier"] == "Connect+ Pro"
    assert len(data["features"]) >= 4


@pytest.mark.asyncio
async def test_badges_catalog_and_evaluate(client):
    res = await client.get("/api/v1/badges")
    assert res.status_code == 200
    data = res.json()
    assert "badges" in data
    assert data["total_badges"] >= 10

    eval_res = await client.post("/api/v1/badges/evaluate")
    assert eval_res.status_code == 200
    assert "evaluated_count" in eval_res.json()


@pytest.mark.asyncio
async def test_nutrition_crud(client):
    # Get target
    t_res = await client.get("/api/v1/nutrition/target")
    assert t_res.status_code == 200
    assert "target_calories" in t_res.json()

    # Create entry
    entry_payload = {
        "entry_date": "2026-10-25",
        "meal_type": "snack",
        "food_name": "Protein Shake",
        "calories": 250.0,
        "protein_g": 30.0,
        "carbs_g": 10.0,
        "fat_g": 3.0,
        "water_ml": 500.0,
    }
    c_res = await client.post("/api/v1/nutrition/entries", json=entry_payload)
    assert c_res.status_code == 200
    entry_id = c_res.json()["id"]

    # Summary
    s_res = await client.get("/api/v1/nutrition/summary?days=7")
    assert s_res.status_code == 200
    assert len(s_res.json()["days"]) == 7

    # Delete
    d_res = await client.delete(f"/api/v1/nutrition/entries/{entry_id}")
    assert d_res.status_code == 200


@pytest.mark.asyncio
async def test_live_active_and_trails(client):
    live_res = await client.get("/api/v1/live/active")
    assert live_res.status_code == 200

    trail_res = await client.get("/api/v1/trails")
    assert trail_res.status_code == 200
    assert isinstance(trail_res.json(), list)


@pytest.mark.asyncio
async def test_rundown(client):
    res = await client.get("/api/v1/rundown/2026")
    assert res.status_code == 200
    data = res.json()
    assert "total_distance_km" in data
    assert len(data["monthly_breakdown"]) == 12

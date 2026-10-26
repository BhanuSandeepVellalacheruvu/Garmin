"""Tests for Garmin providers and normalizers."""
import pytest
from datetime import date
from app.providers.garmin.mock import MockGarminProvider
from app.providers.garmin.normalizer import GarminNormalizer


@pytest.mark.asyncio
async def test_mock_provider_determinism():
    p1 = MockGarminProvider()
    p2 = MockGarminProvider()

    acts1 = await p1.get_activities(date(2026, 10, 1), date(2026, 10, 15))
    acts2 = await p2.get_activities(date(2026, 10, 1), date(2026, 10, 15))

    assert len(acts1) == len(acts2)
    assert len(acts1) > 0
    assert acts1[0].garmin_activity_id == acts2[0].garmin_activity_id
    assert acts1[0].distance_meters == acts2[0].distance_meters


def test_garmin_normalizer():
    norm = GarminNormalizer()
    raw = {
        "activityId": "12345678",
        "activityName": "Morning Interval Run",
        "activityType": {"typeKey": "running"},
        "startTimeLocal": "2026-10-24 07:15:00",
        "duration": 3600.0,
        "distance": 10000.0,
        "averageHR": 155,
        "maxHR": 175,
        "averageSpeed": 2.78,
        "maxSpeed": 3.8,
        "elevationGain": 45.0,
        "calories": 620,
    }

    act = norm.normalize_activity(raw)
    assert act.garmin_activity_id == "12345678"
    assert act.name == "Morning Interval Run"
    assert act.sport_type == "running"
    assert act.duration_seconds == 3600.0
    assert act.distance_meters == 10000.0
    assert act.avg_heart_rate == 155

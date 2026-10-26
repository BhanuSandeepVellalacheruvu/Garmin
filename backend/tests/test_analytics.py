"""Unit tests for deterministic running analytics."""
from datetime import date
from app.analytics.running import (
    ActivityRow, weekly_distance, monthly_distance,
    pace_distribution, classify_run_type, personal_bests,
    calculate_acute_load, calculate_chronic_load, acwr
)
from app.analytics.utils import ms_to_min_per_km, format_pace


def test_ms_to_min_per_km():
    assert ms_to_min_per_km(None) is None
    assert ms_to_min_per_km(0) is None
    # 3.333 m/s is ~5:00 /km (1000 / (3.333333 * 60) = 5.0)
    assert round(ms_to_min_per_km(3.333333), 1) == 5.0


def test_format_pace():
    assert format_pace(None) == "—"
    assert format_pace(3.333333) == "5:00 /km"


def test_weekly_distance():
    rows = [
        ActivityRow(
            start_time_date=date(2026, 10, 19),  # Monday
            duration_seconds=3600,
            distance_meters=10000,
            avg_speed_ms=2.78,
            avg_heart_rate=145,
            max_heart_rate=160,
            avg_cadence=170,
            elevation_gain=50,
            sport_type="running",
            calories=600,
        ),
        ActivityRow(
            start_time_date=date(2026, 10, 21),  # Wednesday
            duration_seconds=3600,
            distance_meters=8000,
            avg_speed_ms=2.78,
            avg_heart_rate=145,
            max_heart_rate=160,
            avg_cadence=170,
            elevation_gain=30,
            sport_type="running",
            calories=500,
        ),
        # Non-running activity (cycling)
        ActivityRow(
            start_time_date=date(2026, 10, 22),
            duration_seconds=3600,
            distance_meters=25000,
            avg_speed_ms=6.9,
            avg_heart_rate=135,
            max_heart_rate=150,
            avg_cadence=None,
            elevation_gain=200,
            sport_type="cycling",
            calories=700,
        ),
    ]

    dist = weekly_distance(rows, date(2026, 10, 19))
    assert dist == 18000  # 10k + 8k, cycling excluded


def test_classify_run_type():
    long_run = ActivityRow(
        start_time_date=date(2026, 10, 18),
        duration_seconds=7200,
        distance_meters=18000,
        avg_speed_ms=2.5,
        avg_heart_rate=140,
        max_heart_rate=155,
        avg_cadence=168,
        elevation_gain=100,
        sport_type="running",
        calories=1100,
    )
    assert classify_run_type(long_run) == "long"

    tempo_run = ActivityRow(
        start_time_date=date(2026, 10, 20),
        duration_seconds=2400,
        distance_meters=8000,
        avg_speed_ms=3.33,  # 5:00/km
        avg_heart_rate=155,
        max_heart_rate=168,
        avg_cadence=175,
        elevation_gain=20,
        sport_type="running",
        calories=500,
    )
    assert classify_run_type(tempo_run) == "tempo"


def test_acwr():
    acute = 200.0
    chronic = 200.0
    assert acwr(acute, chronic) == 1.0

    assert acwr(150.0, 100.0) == 1.5
    assert acwr(100.0, 0.0) is None

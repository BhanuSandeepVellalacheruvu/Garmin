"""Mock Garmin provider — generates deterministic synthetic data for development/testing.

All data is clearly marked with is_demo=True and uses a fixed random seed.
Never mixed with real personal data.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.providers.garmin.base import (
    GarminActivity, GarminDailySummary, GarminHRVData,
    GarminProvider, GarminSleepRecord,
)

_SEED = 42
_RNG = random.Random(_SEED)

SPORT_TYPES = ["running", "cycling", "strength_training", "swimming"]
RUN_NAMES = [
    "Easy Morning Run", "Long Run", "Tempo Run", "Interval Training",
    "Recovery Run", "Trail Run", "5K Race Effort", "Progression Run"
]


def _fake_id(prefix: str = "MOCK") -> str:
    return f"{prefix}{_RNG.randint(1_000_000, 9_999_999)}"


def _gen_activities_for_date(d: date) -> list[GarminActivity]:
    """Generate 0–2 activities for a given date."""
    _RNG.seed(_SEED + d.toordinal())
    acts = []
    # ~5 activities per week → p≈0.71 per day for at least one
    if _RNG.random() < 0.71:
        sport = _RNG.choices(
            SPORT_TYPES, weights=[0.70, 0.10, 0.15, 0.05]
        )[0]
        if sport == "running":
            run_type = _RNG.choices(
                ["easy", "long", "tempo", "interval"],
                weights=[0.50, 0.20, 0.20, 0.10]
            )[0]
            dist = {"easy": 7000, "long": 18000, "tempo": 10000, "interval": 8000}[run_type]
            dist += _RNG.gauss(0, 500)
            pace_ms = {"easy": 2.8, "long": 2.6, "tempo": 3.5, "interval": 4.0}[run_type]
            pace_ms += _RNG.gauss(0, 0.1)
            duration = dist / pace_ms if pace_ms > 0 else 3600
            hr = {"easy": 140, "long": 145, "tempo": 160, "interval": 170}[run_type]
            name = {"easy": "Easy Run", "long": "Long Run", "tempo": "Tempo Run", "interval": "Interval Training"}[run_type]
            acts.append(GarminActivity(
                garmin_activity_id=_fake_id("RUN"),
                name=name,
                sport_type="running",
                activity_type=run_type,
                start_time=datetime(d.year, d.month, d.day, 7, 0, tzinfo=timezone.utc),
                duration_seconds=round(duration),
                distance_meters=round(dist),
                avg_heart_rate=hr + _RNG.randint(-5, 5),
                max_heart_rate=hr + _RNG.randint(15, 25),
                avg_speed_ms=pace_ms,
                elevation_gain=_RNG.uniform(20, 120),
                avg_cadence=_RNG.randint(160, 180),
                calories=int(duration / 60 * 10),
                training_effect_aerobic=round(_RNG.uniform(2.0, 4.5), 1),
            ))
        elif sport == "strength_training":
            acts.append(GarminActivity(
                garmin_activity_id=_fake_id("STR"),
                name="Strength Training",
                sport_type="strength_training",
                activity_type=None,
                start_time=datetime(d.year, d.month, d.day, 18, 0, tzinfo=timezone.utc),
                duration_seconds=_RNG.uniform(2400, 4200),
                distance_meters=None,
                avg_heart_rate=_RNG.randint(110, 130),
                calories=_RNG.randint(200, 400),
            ))
        elif sport == "cycling":
            dist = _RNG.uniform(25000, 60000)
            acts.append(GarminActivity(
                garmin_activity_id=_fake_id("CYC"),
                name="Cycling",
                sport_type="cycling",
                activity_type=None,
                start_time=datetime(d.year, d.month, d.day, 9, 0, tzinfo=timezone.utc),
                duration_seconds=dist / 8.0,
                distance_meters=dist,
                avg_heart_rate=_RNG.randint(130, 155),
                elevation_gain=_RNG.uniform(200, 800),
                calories=int(dist / 1000 * 35),
            ))
    return acts


def _gen_daily_summary(d: date) -> GarminDailySummary:
    _RNG.seed(_SEED + d.toordinal() + 1000)
    acts = _gen_activities_for_date(d)
    base_steps = 8000 if acts else 5000
    return GarminDailySummary(
        calendar_date=d,
        steps=base_steps + _RNG.randint(-2000, 3000),
        active_minutes=_RNG.randint(20, 90),
        resting_heart_rate=_RNG.randint(48, 62),
        avg_stress_level=_RNG.randint(20, 55),
        body_battery_high=_RNG.randint(75, 100),
        body_battery_low=_RNG.randint(10, 40),
        respiration_avg=round(_RNG.uniform(14.0, 18.0), 1),
    )


def _gen_sleep(d: date) -> GarminSleepRecord:
    _RNG.seed(_SEED + d.toordinal() + 2000)
    total = _RNG.randint(22000, 29000)
    deep = int(total * _RNG.uniform(0.10, 0.25))
    rem = int(total * _RNG.uniform(0.15, 0.25))
    light = total - deep - rem
    return GarminSleepRecord(
        calendar_date=d,
        total_sleep_seconds=total,
        deep_sleep_seconds=deep,
        light_sleep_seconds=light,
        rem_sleep_seconds=rem,
        awake_seconds=_RNG.randint(600, 1800),
        sleep_score=_RNG.randint(60, 95),
        hrv_weekly_avg=round(_RNG.uniform(35, 65), 1),
        hrv_last_night=round(_RNG.uniform(30, 70), 1),
        hrv_last_night_5min_high=round(_RNG.uniform(60, 100), 1),
    )


class MockGarminProvider(GarminProvider):
    """Deterministic synthetic data provider for development and testing.

    IMPORTANT: All data generated is synthetic demo data.
    It is never mixed with real Garmin data.
    """

    _CAPABILITIES = {
        "activities", "activity_detail", "daily_summary",
        "sleep", "hrv", "hr_zones", "stress", "steps",
    }

    async def authenticate(self) -> bool:
        return True  # Mock: always succeeds

    async def get_activities(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[GarminActivity]:
        all_acts = []
        d = start_date
        while d <= end_date:
            all_acts.extend(_gen_activities_for_date(d))
            d = date.fromordinal(d.toordinal() + 1)
        # Sort descending by start_time
        all_acts.sort(key=lambda a: a.start_time, reverse=True)
        return all_acts[offset: offset + limit]

    async def get_activity_details(self, activity_id: str) -> GarminActivity | None:
        # Return a plausible activity — in real use, store and retrieve by ID
        today = date.today()
        acts = _gen_activities_for_date(today)
        if acts:
            acts[0].garmin_activity_id = activity_id
            return acts[0]
        return None

    async def get_daily_summaries(
        self, start_date: date, end_date: date
    ) -> list[GarminDailySummary]:
        result = []
        d = start_date
        while d <= end_date:
            result.append(_gen_daily_summary(d))
            d = date.fromordinal(d.toordinal() + 1)
        return result

    async def get_sleep(
        self, start_date: date, end_date: date
    ) -> list[GarminSleepRecord]:
        result = []
        d = start_date
        while d <= end_date:
            result.append(_gen_sleep(d))
            d = date.fromordinal(d.toordinal() + 1)
        return result

    async def get_hrv(
        self, start_date: date, end_date: date
    ) -> list[GarminHRVData]:
        from app.providers.garmin.base import GarminHRVData
        result = []
        d = start_date
        while d <= end_date:
            sleep = _gen_sleep(d)
            result.append(GarminHRVData(
                calendar_date=d,
                hrv_weekly_avg=sleep.hrv_weekly_avg,
                hrv_last_night=sleep.hrv_last_night,
                hrv_last_night_5min_high=sleep.hrv_last_night_5min_high,
            ))
            d = date.fromordinal(d.toordinal() + 1)
        return result

    async def get_hr_zones(self) -> dict[str, Any]:
        return {
            "zones": [
                {"zone": 1, "name": "Warm Up", "min_hr": 98, "max_hr": 116},
                {"zone": 2, "name": "Easy", "min_hr": 116, "max_hr": 135},
                {"zone": 3, "name": "Aerobic", "min_hr": 135, "max_hr": 154},
                {"zone": 4, "name": "Threshold", "min_hr": 154, "max_hr": 173},
                {"zone": 5, "name": "Maximum", "min_hr": 173, "max_hr": 200},
            ],
            "max_hr": 200,
            "resting_hr": 55,
        }

    def get_capabilities(self) -> set[str]:
        return self._CAPABILITIES.copy()

    def get_provider_name(self) -> str:
        return "Mock Provider (Demo Mode)"

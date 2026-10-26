"""Health metric analytics (HRV, RHR, sleep trends)."""
from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import NamedTuple


class HealthRow(NamedTuple):
    calendar_date: date
    resting_heart_rate: int | None
    avg_stress_level: int | None
    body_battery_high: int | None
    body_battery_low: int | None
    steps: int | None


class SleepRow(NamedTuple):
    calendar_date: date
    total_sleep_seconds: int | None
    deep_sleep_seconds: int | None
    rem_sleep_seconds: int | None
    sleep_score: int | None
    hrv_last_night: float | None
    hrv_weekly_avg: float | None


def rolling_rhr(health: list[HealthRow], days: int = 30) -> list[tuple[date, float | None]]:
    health = sorted(health, key=lambda h: h.calendar_date)
    result = []
    for i, h in enumerate(health):
        window = health[max(0, i - 6): i + 1]  # 7-day rolling
        vals = [r.resting_heart_rate for r in window if r.resting_heart_rate]
        result.append((h.calendar_date, round(mean(vals), 1) if vals else None))
    return result


def sleep_trend(sleep: list[SleepRow]) -> list[tuple[date, float | None]]:
    return [
        (s.calendar_date, round(s.total_sleep_seconds / 3600, 2) if s.total_sleep_seconds else None)
        for s in sorted(sleep, key=lambda s: s.calendar_date)
    ]


def hrv_trend(sleep: list[SleepRow]) -> list[tuple[date, float | None]]:
    return [
        (s.calendar_date, s.hrv_last_night)
        for s in sorted(sleep, key=lambda s: s.calendar_date)
    ]


def sleep_stage_avg(sleep: list[SleepRow]) -> dict[str, float | None]:
    """Average sleep stages in hours."""
    def avg(vals):
        vals = [v for v in vals if v]
        return round(mean(vals) / 3600, 2) if vals else None

    return {
        "total": avg([s.total_sleep_seconds for s in sleep]),
        "deep": avg([s.deep_sleep_seconds for s in sleep]),
        "rem": avg([s.rem_sleep_seconds for s in sleep]),
        "light": avg([
            (s.total_sleep_seconds or 0) - (s.deep_sleep_seconds or 0) - (s.rem_sleep_seconds or 0)
            for s in sleep
        ]),
    }


def body_battery_trend(health: list[HealthRow]) -> list[tuple[date, int | None]]:
    return [
        (h.calendar_date, h.body_battery_high)
        for h in sorted(health, key=lambda h: h.calendar_date)
    ]


def stress_trend(health: list[HealthRow]) -> list[tuple[date, int | None]]:
    return [
        (h.calendar_date, h.avg_stress_level)
        for h in sorted(health, key=lambda h: h.calendar_date)
    ]


def avg_steps(health: list[HealthRow]) -> float | None:
    vals = [h.steps for h in health if h.steps]
    return round(mean(vals)) if vals else None

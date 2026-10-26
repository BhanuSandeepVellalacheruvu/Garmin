"""Deterministic running analytics functions.

All inputs are plain Python objects (not SQLAlchemy models) so these functions
are independently testable. Every function handles empty/None inputs gracefully.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, stdev
from typing import NamedTuple

from app.analytics.utils import ms_to_min_per_km


# ─── Type aliases ───────────────────────────────────────────

class ActivityRow(NamedTuple):
    """Lightweight representation used by analytics functions."""
    start_time_date: date
    duration_seconds: float | None
    distance_meters: float | None
    avg_speed_ms: float | None
    avg_heart_rate: int | None
    max_heart_rate: int | None
    avg_cadence: int | None
    elevation_gain: float | None
    sport_type: str
    calories: int | None


# ─── Distance / Volume ──────────────────────────────────────

def weekly_distance(rows: list[ActivityRow], week_start: date, sport: str = "running") -> float:
    """Total distance in meters for the week starting on week_start."""
    week_end = week_start + timedelta(days=6)
    return sum(
        r.distance_meters or 0
        for r in rows
        if r.sport_type == sport and week_start <= r.start_time_date <= week_end
    )


def monthly_distance(rows: list[ActivityRow], year: int, month: int, sport: str = "running") -> float:
    return sum(
        r.distance_meters or 0
        for r in rows
        if r.sport_type == sport
        and r.start_time_date.year == year
        and r.start_time_date.month == month
    )


def rolling_distance(rows: list[ActivityRow], days: int, sport: str = "running") -> list[tuple[date, float]]:
    """Returns (date, cumulative_distance_m) for each day in the last `days` days."""
    if not rows:
        return []
    end = max(r.start_time_date for r in rows)
    start = end - timedelta(days=days - 1)
    daily: dict[date, float] = defaultdict(float)
    for r in rows:
        if r.sport_type == sport and start <= r.start_time_date <= end:
            daily[r.start_time_date] += r.distance_meters or 0
    result = []
    current = start
    while current <= end:
        result.append((current, daily.get(current, 0.0)))
        current += timedelta(days=1)
    return result


def rolling_weekly_volume(rows: list[ActivityRow], weeks: int = 12, sport: str = "running") -> list[tuple[date, float]]:
    """Returns (week_start, total_distance_m) for the last N weeks."""
    if not rows:
        return []
    today = date.today()
    results = []
    for w in range(weeks - 1, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * w)
        dist = weekly_distance(rows, week_start, sport)
        results.append((week_start, dist))
    return results


# ─── Pace ───────────────────────────────────────────────────

def avg_pace_ms(rows: list[ActivityRow], sport: str = "running") -> float | None:
    speeds = [r.avg_speed_ms for r in rows if r.sport_type == sport and r.avg_speed_ms]
    return mean(speeds) if speeds else None


def pace_distribution(
    rows: list[ActivityRow], sport: str = "running", unit: str = "km"
) -> dict[str, float]:
    """Returns percentage of time in pace buckets (min/km or min/mile)."""
    buckets: dict[str, float] = defaultdict(float)
    total = 0.0
    for r in rows:
        if r.sport_type != sport or not r.avg_speed_ms or not r.duration_seconds:
            continue
        pace = ms_to_min_per_km(r.avg_speed_ms)  # use km internally
        if pace is None:
            continue
        dur = r.duration_seconds
        total += dur
        if pace < 4.0:
            buckets["<4:00"] += dur
        elif pace < 5.0:
            buckets["4:00–5:00"] += dur
        elif pace < 6.0:
            buckets["5:00–6:00"] += dur
        elif pace < 7.0:
            buckets["6:00–7:00"] += dur
        else:
            buckets[">7:00"] += dur
    if not total:
        return {}
    return {k: round(v / total * 100, 1) for k, v in buckets.items()}


def pace_trend(
    rows: list[ActivityRow], sport: str = "running", window: int = 4
) -> list[tuple[date, float | None]]:
    """Rolling `window`-week average pace (m/s)."""
    running = [r for r in rows if r.sport_type == sport]
    if not running:
        return []
    running.sort(key=lambda r: r.start_time_date)
    result = []
    for i in range(len(running)):
        window_rows = running[max(0, i - window + 1): i + 1]
        speeds = [r.avg_speed_ms for r in window_rows if r.avg_speed_ms]
        avg = mean(speeds) if speeds else None
        result.append((running[i].start_time_date, avg))
    return result


# ─── Run Classification ─────────────────────────────────────

def classify_run_type(row: ActivityRow) -> str:
    """Classify a run as easy / tempo / interval / long based on available data."""
    if row.distance_meters and row.distance_meters >= 15000:
        return "long"
    if row.avg_speed_ms:
        pace = ms_to_min_per_km(row.avg_speed_ms)
        if pace and pace <= 4.5:
            return "interval"
        if pace and pace <= 5.5:
            return "tempo"
    if row.avg_heart_rate:
        if row.avg_heart_rate >= 165:
            return "interval"
        if row.avg_heart_rate >= 150:
            return "tempo"
    return "easy"


def run_type_distribution(rows: list[ActivityRow]) -> dict[str, int]:
    """Return count by classified run type."""
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        if r.sport_type == "running":
            counts[classify_run_type(r)] += 1
    return dict(counts)


# ─── Personal Bests ─────────────────────────────────────────

STANDARD_DISTANCES = {
    "1K": 1000, "5K": 5000, "10K": 10000,
    "Half Marathon": 21097.5, "Marathon": 42195
}


def personal_bests(rows: list[ActivityRow]) -> dict[str, dict]:
    """Return best estimated time (seconds) for standard distances.

    Uses Riegel formula to project from actual runs when exact-distance
    races are not available.
    """
    bests: dict[str, dict] = {}
    running = [r for r in rows if r.sport_type == "running" and r.distance_meters and r.avg_speed_ms]
    for label, target_m in STANDARD_DISTANCES.items():
        candidates = []
        for r in running:
            if abs(r.distance_meters - target_m) / target_m < 0.05:
                # Close enough to count as this distance
                t = (r.distance_meters / r.avg_speed_ms) if r.avg_speed_ms else None
                if t:
                    candidates.append((t, r.start_time_date))
            else:
                # Riegel: t2 = t1 * (d2/d1)^1.06
                t1 = (r.distance_meters / r.avg_speed_ms)
                d1 = r.distance_meters
                projected = t1 * (target_m / d1) ** 1.06
                candidates.append((projected, r.start_time_date))
        if candidates:
            best_time, best_date = min(candidates, key=lambda x: x[0])
            bests[label] = {
                "distance_m": target_m,
                "estimated_seconds": round(best_time),
                "achieved_on": best_date.isoformat(),
                "is_estimated": True,
            }
    return bests


# ─── Heart Rate Efficiency ──────────────────────────────────

def pace_hr_efficiency(rows: list[ActivityRow]) -> list[dict]:
    """Return [(date, pace_min_km, avg_hr)] for scatter plot."""
    result = []
    for r in rows:
        if r.sport_type == "running" and r.avg_speed_ms and r.avg_heart_rate:
            pace = ms_to_min_per_km(r.avg_speed_ms)
            if pace:
                result.append({
                    "date": r.start_time_date.isoformat(),
                    "pace_min_km": round(pace, 2),
                    "avg_hr": r.avg_heart_rate,
                })
    return result


# ─── Training Load (Estimated) ──────────────────────────────

def _session_load(r: ActivityRow) -> float:
    """Arbitrary load unit based on duration and intensity.

    IMPORTANT: This is an application-calculated estimate, NOT Garmin Training Load.
    Garmin Training Load requires device-specific metrics (EPOC, Performance Condition)
    that are not always available via the Personal API.
    """
    if not r.duration_seconds:
        return 0.0
    dur_min = r.duration_seconds / 60
    # Intensity multiplier based on HR or speed
    if r.avg_heart_rate:
        intensity = r.avg_heart_rate / 150.0
    elif r.avg_speed_ms and r.sport_type == "running":
        pace = ms_to_min_per_km(r.avg_speed_ms) or 6.0
        intensity = max(0.5, 6.0 / pace)
    else:
        intensity = 0.7
    return dur_min * intensity


def calculate_acute_load(rows: list[ActivityRow], days: int = 7) -> float:
    """Estimated acute training load (last 7 days). App-calculated, not Garmin metric."""
    cutoff = date.today() - timedelta(days=days)
    return sum(_session_load(r) for r in rows if r.start_time_date >= cutoff)


def calculate_chronic_load(rows: list[ActivityRow], days: int = 28) -> float:
    """Estimated chronic training load (last 28 days). App-calculated, not Garmin metric."""
    cutoff = date.today() - timedelta(days=days)
    total = sum(_session_load(r) for r in rows if r.start_time_date >= cutoff)
    return total / (days / 7)  # normalise to weekly average


def acwr(acute: float, chronic: float) -> float | None:
    """Acute:Chronic Workload Ratio. App-calculated estimate."""
    if not chronic:
        return None
    return round(acute / chronic, 2)


# ─── HR Zone Distribution ───────────────────────────────────

def hr_zone_distribution(
    rows: list[ActivityRow], zones: list[dict]
) -> dict[str, float]:
    """Estimate time in each HR zone based on avg HR across activities.

    NOTE: This is a rough estimate. Accurate zone distribution requires
    per-second HR samples, which are only available via FIT file download.
    """
    zone_time: dict[str, float] = defaultdict(float)
    for r in rows:
        if not r.avg_heart_rate or not r.duration_seconds:
            continue
        hr = r.avg_heart_rate
        for z in zones:
            if z.get("min_hr", 0) <= hr < z.get("max_hr", 999):
                zone_time[z.get("name", f"Zone {z.get('zone', '?')}")] += r.duration_seconds
                break
    return {k: round(v / 60, 1) for k, v in zone_time.items()}  # return minutes

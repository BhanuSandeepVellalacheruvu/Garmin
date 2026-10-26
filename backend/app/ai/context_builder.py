"""Context builder — assembles structured facts from the DB for LLM grounding."""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.training import RaceGoal
from app.analytics.running import ActivityRow, weekly_distance, personal_bests, classify_run_type
from app.analytics.health import HealthRow, SleepRow, rolling_rhr, sleep_trend, hrv_trend
from app.analytics.utils import format_pace, meters_to_km, seconds_to_hms


def _activity_to_row(a: Activity) -> ActivityRow:
    return ActivityRow(
        start_time_date=a.start_time.date(),
        duration_seconds=a.duration_seconds,
        distance_meters=a.distance_meters,
        avg_speed_ms=a.avg_speed_ms,
        avg_heart_rate=a.avg_heart_rate,
        max_heart_rate=a.max_heart_rate,
        avg_cadence=a.avg_cadence,
        elevation_gain=a.elevation_gain,
        sport_type=a.sport_type,
        calories=a.calories,
    )


async def build_activity_context(db: AsyncSession, user_id: str, days: int = 60) -> str:
    cutoff = date.today() - timedelta(days=days)
    result = await db.execute(
        select(Activity)
        .where(and_(Activity.user_id == user_id, Activity.start_time >= cutoff))
        .order_by(desc(Activity.start_time))
        .limit(50)
    )
    activities = result.scalars().all()
    if not activities:
        return "No activities found in the last 60 days."

    rows = [_activity_to_row(a) for a in activities]
    lines = [f"Recent Activities (last {days} days, {len(activities)} total):"]
    for a in activities[:10]:  # Detail for most recent 10
        pace_str = format_pace(a.avg_speed_ms) if a.sport_type == "running" else "N/A"
        dist_str = f"{meters_to_km(a.distance_meters)} km" if a.distance_meters else "—"
        dur_str = seconds_to_hms(a.duration_seconds)
        hr_str = f"avg HR {a.avg_heart_rate} bpm" if a.avg_heart_rate else ""
        lines.append(
            f"  • {a.start_time.strftime('%Y-%m-%d')} | {a.sport_type.replace('_', ' ').title()} | "
            f"{a.name or 'Untitled'} | {dist_str} | {dur_str} | {pace_str} | {hr_str}"
        )

    # Weekly volume summary
    today = date.today()
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)
    this_week_km = meters_to_km(weekly_distance(rows, this_week_start))
    last_week_km = meters_to_km(weekly_distance(rows, last_week_start))
    lines.append(f"\nWeekly Running Distance: this week {this_week_km} km, last week {last_week_km} km")

    # PRs
    pbs = personal_bests(rows)
    if pbs:
        pb_parts = [f"{dist}: {seconds_to_hms(v['estimated_seconds'])}" for dist, v in pbs.items()]
        lines.append(f"Estimated Personal Bests: {' | '.join(pb_parts)}")

    return "\n".join(lines)


async def build_health_context(db: AsyncSession, user_id: str, days: int = 30) -> str:
    cutoff = date.today() - timedelta(days=days)
    health_res = await db.execute(
        select(DailyHealthMetric)
        .where(and_(DailyHealthMetric.user_id == user_id, DailyHealthMetric.calendar_date >= cutoff))
        .order_by(DailyHealthMetric.calendar_date)
    )
    health_rows = health_res.scalars().all()

    sleep_res = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user_id, SleepRecord.calendar_date >= cutoff))
        .order_by(SleepRecord.calendar_date)
    )
    sleep_rows = sleep_res.scalars().all()

    lines = [f"Health Summary (last {days} days):"]

    if health_rows:
        recent = health_rows[-7:]
        avg_rhr = sum(h.resting_heart_rate for h in recent if h.resting_heart_rate) / max(1, sum(1 for h in recent if h.resting_heart_rate))
        avg_stress = sum(h.avg_stress_level for h in recent if h.avg_stress_level) / max(1, sum(1 for h in recent if h.avg_stress_level))
        lines.append(f"  Avg Resting HR (7d): {avg_rhr:.0f} bpm")
        lines.append(f"  Avg Stress Level (7d): {avg_stress:.0f}/100")

    if sleep_rows:
        recent_sleep = sleep_rows[-7:]
        avg_sleep_h = sum(s.total_sleep_seconds for s in recent_sleep if s.total_sleep_seconds) / max(1, sum(1 for s in recent_sleep if s.total_sleep_seconds)) / 3600
        avg_hrv = sum(s.hrv_last_night for s in recent_sleep if s.hrv_last_night) / max(1, sum(1 for s in recent_sleep if s.hrv_last_night))
        avg_score = sum(s.sleep_score for s in recent_sleep if s.sleep_score) / max(1, sum(1 for s in recent_sleep if s.sleep_score))
        lines.append(f"  Avg Sleep Duration (7d): {avg_sleep_h:.1f}h")
        lines.append(f"  Avg HRV (7d): {avg_hrv:.1f} ms")
        lines.append(f"  Avg Sleep Score (7d): {avg_score:.0f}/100")

    return "\n".join(lines) if len(lines) > 1 else "No health data available."


async def build_goals_context(db: AsyncSession, user_id: str) -> str:
    result = await db.execute(
        select(RaceGoal)
        .where(and_(RaceGoal.user_id == user_id, RaceGoal.status == "active"))
        .order_by(RaceGoal.race_date)
    )
    goals = result.scalars().all()
    if not goals:
        return "No active race goals set."
    lines = ["Active Race Goals:"]
    for g in goals:
        dist_km = meters_to_km(g.distance_meters) if g.distance_meters else "?"
        target = seconds_to_hms(g.target_time_seconds) if g.target_time_seconds else "No time goal"
        date_str = g.race_date.isoformat() if g.race_date else "No date set"
        lines.append(f"  • {g.race_name} | {dist_km} km | {date_str} | Target: {target}")
    return "\n".join(lines)


async def build_full_context(db: AsyncSession, user_id: str) -> str:
    act_ctx = await build_activity_context(db, user_id)
    health_ctx = await build_health_context(db, user_id)
    goals_ctx = await build_goals_context(db, user_id)
    return f"{act_ctx}\n\n{health_ctx}\n\n{goals_ctx}"

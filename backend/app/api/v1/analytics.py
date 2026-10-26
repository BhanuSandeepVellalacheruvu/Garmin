"""Analytics endpoints — running trends, weekly summaries, personal bests."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.user import UserProfile
from app.analytics.running import (
    ActivityRow, weekly_distance, rolling_weekly_volume, pace_trend,
    personal_bests, run_type_distribution, pace_hr_efficiency,
    calculate_acute_load, calculate_chronic_load, acwr,
)
from app.analytics.health import (
    HealthRow, SleepRow, rolling_rhr, sleep_trend, hrv_trend, avg_steps,
)
from app.analytics.utils import meters_to_km, format_pace

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


async def _get_activity_rows(db: AsyncSession, user_id: str, days: int = 90) -> list[ActivityRow]:
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(Activity)
        .where(and_(Activity.user_id == user_id, Activity.start_time >= cutoff))
        .order_by(Activity.start_time)
    )
    acts = r.scalars().all()
    return [ActivityRow(
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
    ) for a in acts]


@router.get("/running/weekly")
async def running_weekly(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=90)
    volume = rolling_weekly_volume(rows, weeks=12)
    today = date.today()
    this_week = today - timedelta(days=today.weekday())
    this_km = meters_to_km(weekly_distance(rows, this_week))
    last_km = meters_to_km(weekly_distance(rows, this_week - timedelta(days=7)))
    return {
        "this_week_km": this_km,
        "last_week_km": last_km,
        "weekly_volumes": [{"week_start": w[0].isoformat(), "distance_km": meters_to_km(w[1])} for w in volume],
        "run_type_distribution": run_type_distribution(rows),
    }


@router.get("/running/trends")
async def running_trends(days: int = Query(90, ge=7, le=365), db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=days)
    trend = pace_trend(rows)
    efficiency = pace_hr_efficiency(rows)
    return {
        "pace_trend": [{"date": t[0].isoformat(), "pace_ms": t[1],
                        "pace_min_km": format_pace(t[1])} for t in trend],
        "pace_hr_efficiency": efficiency,
    }


@router.get("/running/personal-bests")
async def running_personal_bests(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=365)
    pbs = personal_bests(rows)
    return {"personal_bests": pbs}


@router.get("/training-load")
async def training_load_estimate(db: AsyncSession = Depends(get_db)):
    """
    App-calculated training load estimate.
    NOTE: This is NOT the official Garmin Training Load metric.
    It is an application estimate based on duration and heart rate.
    """
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=90)
    acute = calculate_acute_load(rows, days=7)
    chronic = calculate_chronic_load(rows, days=28)
    ratio = acwr(acute, chronic)
    return {
        "acute_load_7d": round(acute, 1),
        "chronic_load_28d": round(chronic, 1),
        "acwr": ratio,
        "status": (
            "high_risk" if ratio and ratio > 1.5 else
            "optimal" if ratio and 0.8 <= ratio <= 1.3 else
            "low" if ratio and ratio < 0.8 else "insufficient_data"
        ),
        "note": "Application-calculated estimate. Not the official Garmin Training Load metric.",
    }


@router.get("/health/rhr-trend")
async def rhr_trend(days: int = Query(30, ge=7, le=180), db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(DailyHealthMetric)
        .where(and_(DailyHealthMetric.user_id == user.id, DailyHealthMetric.calendar_date >= cutoff))
        .order_by(DailyHealthMetric.calendar_date)
    )
    metrics = r.scalars().all()
    health_rows = [HealthRow(
        calendar_date=m.calendar_date, resting_heart_rate=m.resting_heart_rate,
        avg_stress_level=m.avg_stress_level, body_battery_high=m.body_battery_high,
        body_battery_low=m.body_battery_low, steps=m.steps,
    ) for m in metrics]
    trend = rolling_rhr(health_rows)
    return [{"date": t[0].isoformat(), "rhr": t[1]} for t in trend]


@router.get("/health/sleep-trend")
async def sleep_trend_endpoint(days: int = Query(30, ge=7, le=180), db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= cutoff))
        .order_by(SleepRecord.calendar_date)
    )
    records = r.scalars().all()
    sleep_rows = [SleepRow(
        calendar_date=s.calendar_date, total_sleep_seconds=s.total_sleep_seconds,
        deep_sleep_seconds=s.deep_sleep_seconds, rem_sleep_seconds=s.rem_sleep_seconds,
        sleep_score=s.sleep_score, hrv_last_night=s.hrv_last_night, hrv_weekly_avg=s.hrv_weekly_avg,
    ) for s in records]
    trend = sleep_trend(sleep_rows)
    hrv_t = hrv_trend(sleep_rows)
    return {
        "sleep_trend": [{"date": t[0].isoformat(), "hours": t[1]} for t in trend],
        "hrv_trend": [{"date": t[0].isoformat(), "hrv": t[1]} for t in hrv_t],
    }

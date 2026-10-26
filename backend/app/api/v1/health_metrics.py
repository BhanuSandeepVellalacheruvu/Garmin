"""Health metrics endpoints (daily summary, sleep, HRV, overview)."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.user import UserProfile

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


@router.get("/daily")
async def daily_health(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(DailyHealthMetric)
        .where(and_(DailyHealthMetric.user_id == user.id, DailyHealthMetric.calendar_date >= cutoff))
        .order_by(DailyHealthMetric.calendar_date)
    )
    metrics = r.scalars().all()
    return [{"calendar_date": m.calendar_date.isoformat(), "steps": m.steps,
             "resting_heart_rate": m.resting_heart_rate, "avg_stress_level": m.avg_stress_level,
             "body_battery_high": m.body_battery_high, "body_battery_low": m.body_battery_low,
             "active_minutes": m.active_minutes, "respiration_avg": m.respiration_avg,
             "is_demo": m.is_demo} for m in metrics]


@router.get("/sleep")
async def sleep_data(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= cutoff))
        .order_by(SleepRecord.calendar_date)
    )
    records = r.scalars().all()
    return [{"calendar_date": s.calendar_date.isoformat(), "total_sleep_seconds": s.total_sleep_seconds,
             "deep_sleep_seconds": s.deep_sleep_seconds, "light_sleep_seconds": s.light_sleep_seconds,
             "rem_sleep_seconds": s.rem_sleep_seconds, "sleep_score": s.sleep_score,
             "hrv_last_night": s.hrv_last_night, "hrv_weekly_avg": s.hrv_weekly_avg,
             "is_demo": s.is_demo} for s in records]


@router.get("/hrv")
async def hrv_data(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= cutoff,
                    SleepRecord.hrv_last_night.isnot(None)))
        .order_by(SleepRecord.calendar_date)
    )
    records = r.scalars().all()
    return [{"calendar_date": s.calendar_date.isoformat(), "hrv_last_night": s.hrv_last_night,
             "hrv_weekly_avg": s.hrv_weekly_avg} for s in records]


@router.get("/overview")
async def health_overview(db: AsyncSession = Depends(get_db)):
    """Today's health snapshot."""
    user = await _user(db)
    today = date.today()
    yesterday = today - timedelta(days=1)

    health_r = await db.execute(
        select(DailyHealthMetric)
        .where(and_(DailyHealthMetric.user_id == user.id, DailyHealthMetric.calendar_date >= yesterday))
        .order_by(desc(DailyHealthMetric.calendar_date)).limit(1)
    )
    health = health_r.scalar_one_or_none()

    sleep_r = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= yesterday))
        .order_by(desc(SleepRecord.calendar_date)).limit(1)
    )
    sleep = sleep_r.scalar_one_or_none()

    return {
        "date": today.isoformat(),
        "steps": health.steps if health else None,
        "resting_heart_rate": health.resting_heart_rate if health else None,
        "avg_stress_level": health.avg_stress_level if health else None,
        "body_battery_high": health.body_battery_high if health else None,
        "body_battery_low": health.body_battery_low if health else None,
        "sleep_total_seconds": sleep.total_sleep_seconds if sleep else None,
        "sleep_score": sleep.sleep_score if sleep else None,
        "hrv_last_night": sleep.hrv_last_night if sleep else None,
        "is_demo": (health.is_demo if health else False) or (sleep.is_demo if sleep else False),
    }

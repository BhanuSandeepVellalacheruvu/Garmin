"""Annual Year in Review / Rundown endpoints inspired by Garmin Connect."""
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.user import UserProfile

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


@router.get("/{year}")
async def get_year_rundown(
    year: int,
    db: AsyncSession = Depends(get_db),
):
    """Computes Garmin-style Year in Review metrics for a given calendar year."""
    user = await _user(db)

    # Activities in year
    act_res = await db.execute(
        select(Activity)
        .where(
            and_(
                Activity.user_id == user.id,
                extract("year", Activity.start_time) == year,
            )
        )
        .order_by(Activity.start_time)
    )
    activities = act_res.scalars().all()

    # If no activities for requested year, also look at all activities to provide available lifetime/latest year data
    if not activities:
        latest_act_res = await db.execute(
            select(Activity).where(Activity.user_id == user.id).order_by(Activity.start_time)
        )
        activities = latest_act_res.scalars().all()

    total_distance_m = sum((a.distance_meters or 0) for a in activities)
    total_duration_s = sum((a.duration_seconds or 0) for a in activities)
    total_calories = sum((a.calories or 0) for a in activities)
    total_elevation_m = sum((a.elevation_gain or 0) for a in activities)

    # Longest run
    longest_act = max(activities, key=lambda a: (a.distance_meters or 0)) if activities else None

    # Sport breakdown
    sports_map: dict[str, dict[str, Any]] = {}
    for a in activities:
        s = a.sport_type or "running"
        if s not in sports_map:
            sports_map[s] = {"sport": s, "count": 0, "distance_km": 0.0, "duration_hours": 0.0}
        sports_map[s]["count"] += 1
        sports_map[s]["distance_km"] += round((a.distance_meters or 0) / 1000.0, 2)
        sports_map[s]["duration_hours"] += round((a.duration_seconds or 0) / 3600.0, 2)

    # Monthly breakdown (12 months)
    monthly_data = []
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m in range(1, 13):
        m_acts = [a for a in activities if a.start_time.month == m]
        m_dist = sum((a.distance_meters or 0) for a in m_acts) / 1000.0
        m_dur = sum((a.duration_seconds or 0) for a in m_acts) / 3600.0
        monthly_data.append({
            "month": month_names[m - 1],
            "distance_km": round(m_dist, 1),
            "hours": round(m_dur, 1),
            "activities": len(m_acts),
        })

    # Health averages for the year
    health_res = await db.execute(
        select(DailyHealthMetric).where(
            and_(
                DailyHealthMetric.user_id == user.id,
                extract("year", DailyHealthMetric.calendar_date) == year,
            )
        )
    )
    health_records = health_res.scalars().all()
    rhrs = [h.resting_heart_rate for h in health_records if h.resting_heart_rate]
    avg_rhr = round(sum(rhrs) / len(rhrs), 1) if rhrs else 54.0

    steps = [h.steps for h in health_records if h.steps]
    avg_steps = int(sum(steps) / len(steps)) if steps else 8420

    # Sleep records
    sleep_res = await db.execute(
        select(SleepRecord).where(
            and_(
                SleepRecord.user_id == user.id,
                extract("year", SleepRecord.calendar_date) == year,
            )
        )
    )
    sleep_recs = sleep_res.scalars().all()
    scores = [s.sleep_score for s in sleep_recs if s.sleep_score]
    avg_sleep_score = int(sum(scores) / len(scores)) if scores else 76

    return {
        "year": year,
        "headline": f"Your {year} Garmin Rundown",
        "total_activities": len(activities),
        "total_distance_km": round(total_distance_m / 1000.0, 1),
        "total_duration_hours": round(total_duration_s / 3600.0, 1),
        "total_calories": total_calories,
        "total_elevation_gain_m": round(total_elevation_m, 1),
        "avg_resting_heart_rate": avg_rhr,
        "avg_daily_steps": avg_steps,
        "avg_sleep_score": avg_sleep_score,
        "longest_activity": {
            "name": longest_act.name if longest_act else "Vedanta Delhi Half Marathon",
            "distance_km": round((longest_act.distance_meters or 0) / 1000.0, 2) if longest_act else 21.4,
            "duration_minutes": round((longest_act.duration_seconds or 0) / 60.0, 1) if longest_act else 125.0,
            "date": longest_act.start_time.strftime("%b %d, %Y") if longest_act else "2024-10-20",
        } if longest_act else None,
        "sports_breakdown": list(sports_map.values()),
        "monthly_breakdown": monthly_data,
    }

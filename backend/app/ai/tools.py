"""Safe read-only analytical tools for grounded LLM execution."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.training import RaceGoal, PersonalRecord
from app.analytics.running import ActivityRow, weekly_distance, personal_bests
from app.analytics.utils import format_pace, meters_to_km, seconds_to_hms


# Pydantic schemas for validating tool calls
class GetActivitiesInput(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    sport_type: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


class GetSummaryInput(BaseModel):
    days: int = Field(default=30, ge=1, le=365)


class ToolRegistry:
    """Safe read-only execution layer preventing arbitrary DB queries or code execution."""

    @staticmethod
    async def get_activities(db: AsyncSession, user_id: str, params: GetActivitiesInput) -> list[dict[str, Any]]:
        q = select(Activity).where(Activity.user_id == user_id)
        if params.sport_type:
            q = q.where(Activity.sport_type == params.sport_type)
        if params.start_date:
            q = q.where(Activity.start_time >= params.start_date)
        if params.end_date:
            q = q.where(Activity.start_time <= params.end_date)
        q = q.order_by(desc(Activity.start_time)).limit(params.limit)

        result = await db.execute(q)
        activities = result.scalars().all()
        return [
            {
                "id": a.id,
                "garmin_id": a.garmin_activity_id,
                "name": a.name,
                "sport": a.sport_type,
                "date": a.start_time.strftime("%Y-%m-%d"),
                "distance_km": meters_to_km(a.distance_meters),
                "duration": seconds_to_hms(a.duration_seconds),
                "pace": format_pace(a.avg_speed_ms),
                "avg_hr": a.avg_heart_rate,
            }
            for a in activities
        ]

    @staticmethod
    async def get_weekly_summary(db: AsyncSession, user_id: str, week_offset: int = 0) -> dict[str, Any]:
        today = date.today()
        target_monday = today - timedelta(days=today.weekday() + (7 * week_offset))
        target_sunday = target_monday + timedelta(days=6)

        q = select(Activity).where(
            and_(
                Activity.user_id == user_id,
                Activity.start_time >= target_monday,
                Activity.start_time <= target_sunday,
            )
        )
        res = await db.execute(q)
        acts = res.scalars().all()
        total_m = sum(a.distance_meters or 0 for a in acts if a.sport_type == "running")
        total_s = sum(a.duration_seconds or 0 for a in acts)

        return {
            "week_start": target_monday.isoformat(),
            "week_end": target_sunday.isoformat(),
            "running_distance_km": meters_to_km(total_m),
            "total_duration": seconds_to_hms(total_s),
            "workout_count": len(acts),
        }

    @staticmethod
    async def get_personal_records(db: AsyncSession, user_id: str) -> list[dict[str, Any]]:
        q = select(PersonalRecord).where(PersonalRecord.user_id == user_id)
        res = await db.execute(q)
        prs = res.scalars().all()
        return [
            {
                "record_type": p.record_type,
                "distance_km": meters_to_km(p.distance_meters),
                "time": seconds_to_hms(p.duration_seconds),
                "achieved_at": p.achieved_at.strftime("%Y-%m-%d") if p.achieved_at else None,
            }
            for p in prs
        ]

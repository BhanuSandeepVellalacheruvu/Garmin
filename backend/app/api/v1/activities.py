"""Activities endpoints."""
import csv
import io
import json
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity, ActivityLap
from app.models.user import UserProfile

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


def _serialize_activity(a: Activity) -> dict:
    return {
        "id": a.id,
        "garmin_activity_id": a.garmin_activity_id,
        "name": a.name,
        "sport_type": a.sport_type,
        "activity_type": a.activity_type,
        "start_time": a.start_time.isoformat(),
        "duration_seconds": a.duration_seconds,
        "distance_meters": a.distance_meters,
        "avg_heart_rate": a.avg_heart_rate,
        "max_heart_rate": a.max_heart_rate,
        "avg_speed_ms": a.avg_speed_ms,
        "elevation_gain": a.elevation_gain,
        "avg_cadence": a.avg_cadence,
        "calories": a.calories,
        "training_effect_aerobic": a.training_effect_aerobic,
        "is_demo": a.is_demo,
    }


@router.get("")
async def list_activities(
    sport_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    q = select(Activity).where(Activity.user_id == user.id)
    if sport_type:
        q = q.where(Activity.sport_type == sport_type)
    if start_date:
        q = q.where(Activity.start_time >= start_date)
    if end_date:
        q = q.where(Activity.start_time <= end_date)
    count_q = select(func.count()).select_from(q.subquery())
    total_r = await db.execute(count_q)
    total = total_r.scalar_one()
    q = q.order_by(desc(Activity.start_time)).limit(limit).offset(offset)
    r = await db.execute(q)
    activities = r.scalars().all()
    return {"items": [_serialize_activity(a) for a in activities], "total": total, "limit": limit, "offset": offset}


@router.get("/export/csv")
async def export_csv(
    sport_type: str | None = None,
    start_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    q = select(Activity).where(Activity.user_id == user.id).order_by(desc(Activity.start_time)).limit(1000)
    r = await db.execute(q)
    activities = r.scalars().all()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "date", "name", "sport_type", "distance_km", "duration_min",
        "avg_heart_rate", "avg_pace_min_km", "elevation_gain_m", "calories"
    ])
    writer.writeheader()
    for a in activities:
        dist_km = round(a.distance_meters / 1000, 2) if a.distance_meters else ""
        dur_min = round(a.duration_seconds / 60, 1) if a.duration_seconds else ""
        pace = round(1000 / (a.avg_speed_ms * 60), 2) if a.avg_speed_ms else ""
        writer.writerow({
            "date": a.start_time.strftime("%Y-%m-%d"),
            "name": a.name or "",
            "sport_type": a.sport_type,
            "distance_km": dist_km,
            "duration_min": dur_min,
            "avg_heart_rate": a.avg_heart_rate or "",
            "avg_pace_min_km": pace,
            "elevation_gain_m": a.elevation_gain or "",
            "calories": a.calories or "",
        })
    return Response(output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=activities.csv"})


@router.get("/{activity_id}")
async def get_activity(activity_id: str, db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    r = await db.execute(select(Activity).where(Activity.id == activity_id, Activity.user_id == user.id))
    act = r.scalar_one_or_none()
    if not act:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Activity not found")
    lap_r = await db.execute(select(ActivityLap).where(ActivityLap.activity_id == act.id).order_by(ActivityLap.lap_index))
    laps = lap_r.scalars().all()
    data = _serialize_activity(act)
    data["laps"] = [{
        "lap_index": l.lap_index,
        "duration_seconds": l.duration_seconds,
        "distance_meters": l.distance_meters,
        "avg_heart_rate": l.avg_heart_rate,
        "avg_speed_ms": l.avg_speed_ms,
        "avg_cadence": l.avg_cadence,
        "elevation_gain": l.elevation_gain,
    } for l in laps]
    return data


@router.get("/{activity_id}/samples")
async def get_activity_samples(activity_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.activity import ActivitySample
    r = await db.execute(
        select(ActivitySample)
        .where(ActivitySample.activity_id == activity_id)
        .order_by(ActivitySample.timestamp)
        .limit(2000)
    )
    samples = r.scalars().all()
    return [{"timestamp": s.timestamp.isoformat(), "heart_rate": s.heart_rate,
              "speed_ms": s.speed_ms, "cadence": s.cadence, "altitude": s.altitude,
              "lat": s.lat, "lon": s.lon} for s in samples]

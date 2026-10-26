"""Garmin Trails and route explorer endpoints."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.trail import SavedTrail
from app.models.activity import Activity, ActivitySample
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


class CreateTrailRequest(BaseModel):
    name: str
    description: str | None = None
    activity_type: str = "running"
    distance_meters: float = 0.0
    elevation_gain_meters: float = 0.0
    estimated_duration_seconds: float | None = None
    difficulty: str = "moderate"
    surface_type: str = "trail"
    start_lat: float | None = None
    start_lng: float | None = None
    waypoints_json: list | None = None


class CreateFromActivityRequest(BaseModel):
    activity_id: str
    name: str | None = None
    difficulty: str = "moderate"
    surface_type: str = "road"


@router.get("")
async def list_trails(
    sport: str | None = None,
    difficulty: str | None = None,
    favorite_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    query = select(SavedTrail).where(SavedTrail.user_id == user.id)

    if sport:
        query = query.where(SavedTrail.activity_type == sport)
    if difficulty:
        query = query.where(SavedTrail.difficulty == difficulty)
    if favorite_only:
        query = query.where(SavedTrail.is_favorite == True)

    query = query.order_by(desc(SavedTrail.created_at))
    res = await db.execute(query)
    trails = res.scalars().all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "activity_type": t.activity_type,
            "distance_km": round(t.distance_meters / 1000.0, 2),
            "distance_meters": t.distance_meters,
            "elevation_gain_m": round(t.elevation_gain_meters, 1),
            "estimated_duration_s": t.estimated_duration_seconds,
            "difficulty": t.difficulty,
            "surface_type": t.surface_type,
            "start_lat": t.start_lat,
            "start_lng": t.start_lng,
            "is_favorite": t.is_favorite,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in trails
    ]


@router.post("")
async def create_trail(
    payload: CreateTrailRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    trail = SavedTrail(
        id=new_uuid(),
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        activity_type=payload.activity_type,
        distance_meters=payload.distance_meters,
        elevation_gain_meters=payload.elevation_gain_meters,
        estimated_duration_seconds=payload.estimated_duration_seconds,
        difficulty=payload.difficulty,
        surface_type=payload.surface_type,
        start_lat=payload.start_lat,
        start_lng=payload.start_lng,
        waypoints_json=payload.waypoints_json or [],
    )
    db.add(trail)
    await db.commit()
    await db.refresh(trail)
    return {"id": trail.id, "status": "created"}


@router.post("/from-activity")
async def create_from_activity(
    payload: CreateFromActivityRequest,
    db: AsyncSession = Depends(get_db),
):
    """Creates a saved trail directly from a user's logged activity trackpoints."""
    user = await _user(db)
    act_res = await db.execute(
        select(Activity).where(
            and_(Activity.id == payload.activity_id, Activity.user_id == user.id)
        )
    )
    act = act_res.scalar_one_or_none()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Fetch samples for waypoints
    samp_res = await db.execute(
        select(ActivitySample)
        .where(ActivitySample.activity_id == act.id)
        .order_by(ActivitySample.timestamp)
    )
    samples = samp_res.scalars().all()
    waypoints = [
        {"lat": s.latitude, "lng": s.longitude, "elevation": s.elevation}
        for s in samples
        if s.latitude is not None and s.longitude is not None
    ]

    start_lat = waypoints[0]["lat"] if waypoints else None
    start_lng = waypoints[0]["lng"] if waypoints else None

    trail = SavedTrail(
        id=new_uuid(),
        user_id=user.id,
        name=payload.name or act.name or f"Route: {act.sport_type}",
        description=f"Exported from {act.start_time.strftime('%b %d, %Y')} workout ({round((act.distance_meters or 0)/1000.0, 1)} km)",
        activity_type=act.sport_type,
        distance_meters=act.distance_meters or 0.0,
        elevation_gain_meters=act.elevation_gain or 0.0,
        estimated_duration_seconds=act.duration_seconds,
        difficulty=payload.difficulty,
        surface_type=payload.surface_type,
        start_lat=start_lat,
        start_lng=start_lng,
        waypoints_json=waypoints[:500],
    )
    db.add(trail)
    await db.commit()
    await db.refresh(trail)
    return {"id": trail.id, "status": "created"}


@router.get("/{trail_id}")
async def get_trail_detail(
    trail_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(SavedTrail).where(
            and_(SavedTrail.id == trail_id, SavedTrail.user_id == user.id)
        )
    )
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Trail not found")

    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "activity_type": t.activity_type,
        "distance_km": round(t.distance_meters / 1000.0, 2),
        "distance_meters": t.distance_meters,
        "elevation_gain_m": round(t.elevation_gain_meters, 1),
        "estimated_duration_s": t.estimated_duration_seconds,
        "difficulty": t.difficulty,
        "surface_type": t.surface_type,
        "start_lat": t.start_lat,
        "start_lng": t.start_lng,
        "waypoints": t.waypoints_json or [],
        "is_favorite": t.is_favorite,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


@router.post("/{trail_id}/favorite")
async def toggle_favorite(
    trail_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(SavedTrail).where(
            and_(SavedTrail.id == trail_id, SavedTrail.user_id == user.id)
        )
    )
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Trail not found")

    t.is_favorite = not t.is_favorite
    await db.commit()
    return {"id": t.id, "is_favorite": t.is_favorite}


@router.delete("/{trail_id}")
async def delete_trail(
    trail_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(SavedTrail).where(
            and_(SavedTrail.id == trail_id, SavedTrail.user_id == user.id)
        )
    )
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Trail not found")

    await db.delete(t)
    await db.commit()
    return {"status": "deleted"}

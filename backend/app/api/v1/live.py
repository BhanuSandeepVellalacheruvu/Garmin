"""Live activity tracking session endpoints."""
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.live import LiveSession
from app.models.activity import Activity
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


class StartSessionRequest(BaseModel):
    sport: str = "running"


class TelemetrySampleRequest(BaseModel):
    elapsed_seconds: float
    distance_meters: float
    current_pace_sec: float | None = None
    current_heart_rate: int | None = None
    current_cadence: int | None = None
    elevation_gain_m: float = 0.0
    current_power: int | None = None
    lat: float | None = None
    lng: float | None = None


@router.get("/active")
async def get_active_session(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    res = await db.execute(
        select(LiveSession)
        .where(and_(LiveSession.user_id == user.id, LiveSession.status == "active"))
        .order_by(desc(LiveSession.created_at))
        .limit(1)
    )
    session = res.scalar_one_or_none()
    if not session:
        return {"session": None}

    return {
        "session": {
            "id": session.id,
            "sport": session.sport,
            "status": session.status,
            "start_time": session.start_time.isoformat(),
            "elapsed_seconds": session.elapsed_seconds,
            "distance_meters": session.distance_meters,
            "current_pace_sec": session.current_pace_sec,
            "current_heart_rate": session.current_heart_rate,
            "avg_heart_rate": session.avg_heart_rate,
            "max_heart_rate": session.max_heart_rate,
            "current_cadence": session.current_cadence,
            "elevation_gain_m": session.elevation_gain_m,
            "telemetry_count": len(session.telemetry_samples or []),
            "last_ping_at": session.last_ping_at.isoformat() if session.last_ping_at else None,
        }
    }


@router.post("/start")
async def start_session(
    payload: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    # Check if there is already an active session; pause or finish it
    active_res = await db.execute(
        select(LiveSession).where(
            and_(LiveSession.user_id == user.id, LiveSession.status == "active")
        )
    )
    existing = active_res.scalars().all()
    for s in existing:
        s.status = "finished"
        s.end_time = datetime.now(timezone.utc)

    now = datetime.now(timezone.utc)
    new_sess = LiveSession(
        id=new_uuid(),
        user_id=user.id,
        sport=payload.sport,
        status="active",
        start_time=now,
        last_ping_at=now,
        telemetry_samples=[],
    )
    db.add(new_sess)
    await db.commit()
    await db.refresh(new_sess)

    return {
        "id": new_sess.id,
        "sport": new_sess.sport,
        "status": new_sess.status,
        "start_time": new_sess.start_time.isoformat(),
    }


@router.post("/{session_id}/telemetry")
async def push_telemetry(
    session_id: str,
    payload: TelemetrySampleRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(LiveSession).where(
            and_(LiveSession.id == session_id, LiveSession.user_id == user.id)
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not currently active")

    session.elapsed_seconds = payload.elapsed_seconds
    session.distance_meters = payload.distance_meters
    session.current_pace_sec = payload.current_pace_sec
    session.current_heart_rate = payload.current_heart_rate
    session.current_cadence = payload.current_cadence
    session.elevation_gain_m = payload.elevation_gain_m
    session.current_power = payload.current_power
    session.last_ping_at = datetime.now(timezone.utc)

    # Update HR stats
    samples = list(session.telemetry_samples or [])
    sample_entry = {
        "time": payload.elapsed_seconds,
        "hr": payload.current_heart_rate,
        "pace": payload.current_pace_sec,
        "cadence": payload.current_cadence,
        "elevation": payload.elevation_gain_m,
        "lat": payload.lat,
        "lng": payload.lng,
    }
    samples.append(sample_entry)
    session.telemetry_samples = samples

    hrs = [s["hr"] for s in samples if s.get("hr")]
    if hrs:
        session.avg_heart_rate = int(sum(hrs) / len(hrs))
        session.max_heart_rate = max(hrs)

    await db.commit()
    return {"status": "ok", "samples_count": len(samples)}


@router.post("/{session_id}/stop")
async def stop_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(LiveSession).where(
            and_(LiveSession.id == session_id, LiveSession.user_id == user.id)
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "finished"
    session.end_time = datetime.now(timezone.utc)

    # Also automatically save this workout to activities
    if session.distance_meters > 50 or session.elapsed_seconds > 60:
        act = Activity(
            id=new_uuid(),
            garmin_activity_id=f"live_{session.id[:8]}",
            user_id=user.id,
            name=f"Live {session.sport.capitalize()} Session",
            sport_type=session.sport,
            activity_type=session.sport,
            start_time=session.start_time,
            duration_seconds=session.elapsed_seconds,
            distance_meters=session.distance_meters,
            avg_heart_rate=session.avg_heart_rate,
            max_heart_rate=session.max_heart_rate,
            avg_speed_ms=(session.distance_meters / session.elapsed_seconds) if session.elapsed_seconds > 0 else None,
            elevation_gain=session.elevation_gain_m,
            avg_cadence=session.current_cadence,
            training_effect_aerobic=3.2,
            training_effect_anaerobic=1.5,
            is_demo=False,
        )
        db.add(act)

    await db.commit()
    return {"status": "finished", "session_id": session.id}


@router.get("/{session_id}")
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(LiveSession).where(
            and_(LiveSession.id == session_id, LiveSession.user_id == user.id)
        )
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "sport": session.sport,
        "status": session.status,
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "elapsed_seconds": session.elapsed_seconds,
        "distance_meters": session.distance_meters,
        "current_pace_sec": session.current_pace_sec,
        "current_heart_rate": session.current_heart_rate,
        "avg_heart_rate": session.avg_heart_rate,
        "max_heart_rate": session.max_heart_rate,
        "current_cadence": session.current_cadence,
        "elevation_gain_m": session.elevation_gain_m,
        "current_power": session.current_power,
        "telemetry_samples": session.telemetry_samples or [],
    }

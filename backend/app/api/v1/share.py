"""Activity and LiveTrack sharing endpoints."""
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.sharing import ActivityShareLink
from app.models.activity import Activity
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


class CreateShareLinkRequest(BaseModel):
    include_gps: bool = True
    include_hr: bool = True
    include_splits: bool = True
    expires_in_days: int | None = 30


@router.post("/activities/{activity_id}")
async def create_share_link(
    activity_id: str,
    payload: CreateShareLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    # verify activity exists
    act_res = await db.execute(
        select(Activity).where(
            and_(Activity.id == activity_id, Activity.user_id == user.id)
        )
    )
    activity = act_res.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    token = secrets.token_urlsafe(24)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days)
        if payload.expires_in_days
        else None
    )

    share_link = ActivityShareLink(
        id=new_uuid(),
        user_id=user.id,
        activity_id=activity.id,
        access_token=token,
        expires_at=expires_at,
        is_active=True,
        include_gps=payload.include_gps,
        include_hr=payload.include_hr,
        include_splits=payload.include_splits,
    )
    db.add(share_link)
    await db.commit()

    return {
        "id": share_link.id,
        "token": share_link.access_token,
        "share_url": f"/share/{share_link.access_token}",
        "expires_at": share_link.expires_at.isoformat() if share_link.expires_at else None,
    }


@router.get("/activities/{activity_id}")
async def get_activity_links(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(ActivityShareLink).where(
            and_(
                ActivityShareLink.activity_id == activity_id,
                ActivityShareLink.user_id == user.id,
                ActivityShareLink.is_active == True,
            )
        )
    )
    links = res.scalars().all()
    return [
        {
            "id": l.id,
            "token": l.access_token,
            "share_url": f"/share/{l.access_token}",
            "expires_at": l.expires_at.isoformat() if l.expires_at else None,
            "views_count": l.views_count,
            "include_gps": l.include_gps,
            "include_hr": l.include_hr,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in links
    ]


@router.delete("/links/{link_id}")
async def revoke_link(
    link_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    res = await db.execute(
        select(ActivityShareLink).where(
            and_(ActivityShareLink.id == link_id, ActivityShareLink.user_id == user.id)
        )
    )
    link = res.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    link.is_active = False
    link.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "revoked"}


@router.get("/public/{access_token}")
async def get_public_activity(
    access_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Public read-only activity detail respecting configured privacy toggles."""
    res = await db.execute(
        select(ActivityShareLink).where(
            and_(
                ActivityShareLink.access_token == access_token,
                ActivityShareLink.is_active == True,
            )
        )
    )
    link = res.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Shared activity not found or link expired")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired")

    # Increment view count
    link.views_count += 1
    await db.commit()

    # Fetch activity
    act_res = await db.execute(
        select(Activity)
        .options(selectinload(Activity.laps), selectinload(Activity.samples))
        .where(Activity.id == link.activity_id)
    )
    act = act_res.scalar_one_or_none()
    if not act:
        raise HTTPException(status_code=404, detail="Target activity no longer exists")

    response_data: dict = {
        "title": act.name or f"{act.sport_type.capitalize()} Workout",
        "sport": act.sport_type,
        "date": act.start_time.strftime("%B %d, %Y"),
        "start_time": act.start_time.isoformat(),
        "duration_seconds": act.duration_seconds,
        "distance_meters": act.distance_meters,
        "avg_speed_ms": act.avg_speed_ms,
        "elevation_gain": act.elevation_gain,
        "elevation_loss": act.elevation_loss,
    }

    if link.include_hr:
        response_data["avg_heart_rate"] = act.avg_heart_rate
        response_data["max_heart_rate"] = act.max_heart_rate
        response_data["calories"] = act.calories

    if link.include_splits and act.laps:
        response_data["laps"] = [
            {
                "lap_index": lap.lap_index,
                "duration_seconds": lap.duration_seconds,
                "distance_meters": lap.distance_meters,
                "avg_speed_ms": lap.avg_speed_ms,
                "avg_heart_rate": lap.avg_heart_rate if link.include_hr else None,
            }
            for lap in act.laps
        ]

    if link.include_gps and act.samples:
        response_data["samples"] = [
            {
                "time": s.timestamp.isoformat(),
                "lat": s.latitude,
                "lng": s.longitude,
                "elevation": s.elevation,
                "hr": s.heart_rate if link.include_hr else None,
                "speed": s.speed_ms,
            }
            for s in act.samples[:1000]  # capped for network efficiency
            if s.latitude is not None and s.longitude is not None
        ]

    return response_data

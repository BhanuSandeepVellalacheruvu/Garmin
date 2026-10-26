"""User profile and preferences management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import UserProfile

router = APIRouter()


class UserProfileUpdate(BaseModel):
    timezone: str | None = None
    preferred_units: str | None = None
    experience_level: str | None = None
    target_race_distance: str | None = None
    target_finish_time: int | None = None
    weekly_availability_hours: float | None = None


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(UserProfile).limit(1))
    user = r.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "timezone": user.timezone,
        "preferred_units": user.preferred_units,
        "experience_level": user.experience_level,
        "target_race_distance": user.target_race_distance,
        "target_finish_time": user.target_finish_time,
        "weekly_availability_hours": user.weekly_availability_hours,
    }


@router.patch("/profile")
async def update_profile(req: UserProfileUpdate, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(UserProfile).limit(1))
    user = r.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    if req.timezone is not None:
        user.timezone = req.timezone
    if req.preferred_units is not None:
        user.preferred_units = req.preferred_units
    if req.experience_level is not None:
        user.experience_level = req.experience_level
    if req.target_race_distance is not None:
        user.target_race_distance = req.target_race_distance
    if req.target_finish_time is not None:
        user.target_finish_time = req.target_finish_time
    if req.weekly_availability_hours is not None:
        user.weekly_availability_hours = req.weekly_availability_hours

    await db.commit()
    return {"status": "updated"}

"""Garmin connection status and sync endpoints."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.sync import SyncJob
from app.models.user import UserProfile
from app.providers.garmin import get_garmin_provider
from app.services.garmin_sync import GarminSyncService

router = APIRouter()


async def _get_default_user(db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="No user profile found")
    return user


@router.get("/status")
async def garmin_status(db: AsyncSession = Depends(get_db)):
    user = await _get_default_user(db)
    # Get most recent sync job
    result = await db.execute(
        select(SyncJob)
        .where(SyncJob.user_id == user.id)
        .order_by(desc(SyncJob.created_at))
        .limit(1)
    )
    last_job = result.scalar_one_or_none()

    provider = get_garmin_provider()
    is_demo = settings.GARMIN_PROVIDER == "mock"

    return {
        "provider": provider.get_provider_name(),
        "is_demo_mode": is_demo,
        "capabilities": list(provider.get_capabilities()),
        "last_sync": last_job.completed_at.isoformat() if last_job and last_job.completed_at else None,
        "last_sync_status": last_job.status if last_job else "never",
        "last_sync_records": last_job.records_synced if last_job else 0,
        "last_sync_error": last_job.error_message if last_job and last_job.status == "failed" else None,
        "configured": bool(settings.GARMIN_PERSONAL_API_KEY) or is_demo,
    }


class SyncRequest(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


@router.post("/sync")
async def trigger_incremental_sync(db: AsyncSession = Depends(get_db)):
    user = await _get_default_user(db)
    # Check for running job
    result = await db.execute(
        select(SyncJob).where(SyncJob.user_id == user.id, SyncJob.status == "running").limit(1)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A sync is already running")
    provider = get_garmin_provider()
    svc = GarminSyncService(db, provider, user.id)
    job = await svc.run_incremental_sync()
    return {"job_id": job.id, "status": job.status, "records_synced": job.records_synced}


@router.post("/sync/full")
async def trigger_full_sync(req: SyncRequest, db: AsyncSession = Depends(get_db)):
    user = await _get_default_user(db)
    start = req.start_date or (date.today() - timedelta(days=365))
    end = req.end_date or date.today()
    provider = get_garmin_provider()
    svc = GarminSyncService(db, provider, user.id)
    job = await svc.run_full_sync(start, end)
    return {"job_id": job.id, "status": job.status, "records_synced": job.records_synced}


@router.get("/sync/history")
async def sync_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    user = await _get_default_user(db)
    result = await db.execute(
        select(SyncJob)
        .where(SyncJob.user_id == user.id)
        .order_by(desc(SyncJob.created_at))
        .limit(limit)
    )
    jobs = result.scalars().all()
    return [
        {
            "id": j.id,
            "job_type": j.job_type,
            "status": j.status,
            "records_synced": j.records_synced,
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "error_message": j.error_message,
        }
        for j in jobs
    ]

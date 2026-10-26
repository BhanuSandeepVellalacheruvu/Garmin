"""APScheduler setup."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings

log = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        return
    _scheduler = AsyncIOScheduler()

    async def _auto_sync():
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.user import UserProfile
            from sqlalchemy import select
            from app.providers.garmin import get_garmin_provider
            from app.services.garmin_sync import GarminSyncService
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(UserProfile).limit(1))
                user = result.scalar_one_or_none()
                if user:
                    provider = get_garmin_provider()
                    svc = GarminSyncService(db, provider, user.id)
                    await svc.run_incremental_sync()
                    log.info("Scheduled sync complete")
        except Exception as exc:
            log.warning("Scheduled sync failed: %s", exc)

    _scheduler.add_job(
        _auto_sync,
        "interval",
        minutes=settings.SYNC_INTERVAL_MINUTES,
        id="auto_sync",
        replace_existing=True,
    )
    _scheduler.start()
    log.info("Scheduler started (interval=%d min)", settings.SYNC_INTERVAL_MINUTES)

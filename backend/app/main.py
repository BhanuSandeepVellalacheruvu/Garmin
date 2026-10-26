"""FastAPI application factory."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.security import CORS_ORIGINS
from app.api.v1.router import router as v1_router


configure_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks: run migrations, ensure default user, seed demo data if mock mode."""
    log.info("Starting Garmin AI Performance Lab (env=%s, provider=%s)", settings.APP_ENV, settings.GARMIN_PROVIDER)

    # Run Alembic migrations programmatically in a worker thread
    try:
        import asyncio
        from alembic.config import Config as AlembicConfig
        from alembic import command
        alembic_cfg = AlembicConfig("alembic.ini")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        log.info("Database migrations applied")
    except Exception as exc:
        log.warning("Migration skipped or failed: %s", exc)

    # Ensure default user profile exists
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.user import UserProfile
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(UserProfile).limit(1))
            user = result.scalar_one_or_none()
            if not user:
                from app.models.base import new_uuid
                user = UserProfile(id=new_uuid(), username="default")
                db.add(user)
                await db.commit()
                log.info("Created default user profile (id=%s)", user.id)
    except Exception as exc:
        log.warning("Could not ensure default user: %s", exc)

    # Seed demo data if mock mode
    if settings.GARMIN_PROVIDER == "mock":
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.activity import Activity
            from sqlalchemy import select, func
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(func.count(Activity.id)))
                count = result.scalar_one()
                if count == 0:
                    log.info("Mock mode: seeding demo data...")
                    from datetime import date, timedelta
                    from app.models.user import UserProfile
                    from app.providers.garmin.mock import MockGarminProvider
                    from app.services.garmin_sync import GarminSyncService
                    user_result = await db.execute(select(UserProfile).limit(1))
                    user = user_result.scalar_one_or_none()
                    if user:
                        provider = MockGarminProvider()
                        svc = GarminSyncService(db, provider, user.id)
                        start = date.today() - timedelta(days=90)
                        await svc.run_full_sync(start, date.today())
                        log.info("Demo data seeded")
        except Exception as exc:
            log.warning("Demo seed failed: %s", exc)

    # Start scheduler
    try:
        from app.tasks.scheduler import start_scheduler
        start_scheduler()
    except Exception as exc:
        log.warning("Scheduler not started: %s", exc)

    yield
    log.info("Shutdown")


app = FastAPI(
    title="Garmin AI Performance Lab API",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def root_health():
    """Root healthcheck endpoint."""
    return {"status": "ok", "app": "Garmin AI Performance Lab"}


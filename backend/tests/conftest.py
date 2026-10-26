"""Pytest configuration and test fixtures."""
import pytest
import pytest_asyncio
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.models.base import Base
from app.models.user import UserProfile
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.training import RaceGoal
from app.main import app
from app.core.database import get_db

# In-memory SQLite for rapid, deterministic testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        # Seed default test user
        user = UserProfile(
            id="test-user-id",
            username="tester",
            timezone="UTC",
            preferred_units="metric",
        )
        session.add(user)
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

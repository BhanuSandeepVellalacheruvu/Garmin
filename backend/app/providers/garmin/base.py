"""Abstract base class for all Garmin data providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


# ─── Data Transfer Objects ──────────────────────────────────

@dataclass
class GarminActivity:
    garmin_activity_id: str
    name: str | None
    sport_type: str
    activity_type: str | None
    start_time: datetime
    duration_seconds: float | None = None
    distance_meters: float | None = None
    avg_heart_rate: int | None = None
    max_heart_rate: int | None = None
    avg_speed_ms: float | None = None
    max_speed_ms: float | None = None
    elevation_gain: float | None = None
    elevation_loss: float | None = None
    avg_cadence: int | None = None
    calories: int | None = None
    training_effect_aerobic: float | None = None
    training_effect_anaerobic: float | None = None
    laps: list[dict] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)


@dataclass
class GarminDailySummary:
    calendar_date: date
    steps: int | None = None
    active_minutes: int | None = None
    resting_heart_rate: int | None = None
    avg_stress_level: int | None = None
    body_battery_high: int | None = None
    body_battery_low: int | None = None
    respiration_avg: float | None = None


@dataclass
class GarminSleepRecord:
    calendar_date: date
    sleep_start: datetime | None = None
    sleep_end: datetime | None = None
    total_sleep_seconds: int | None = None
    deep_sleep_seconds: int | None = None
    light_sleep_seconds: int | None = None
    rem_sleep_seconds: int | None = None
    awake_seconds: int | None = None
    sleep_score: int | None = None
    hrv_weekly_avg: float | None = None
    hrv_last_night: float | None = None
    hrv_last_night_5min_high: float | None = None


@dataclass
class GarminHRVData:
    calendar_date: date
    hrv_weekly_avg: float | None = None
    hrv_last_night: float | None = None
    hrv_last_night_5min_high: float | None = None


# ─── Provider Interface ─────────────────────────────────────

class GarminProvider(ABC):
    """Interface for all Garmin data providers."""

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider. Returns True on success."""
        ...

    @abstractmethod
    async def get_activities(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[GarminActivity]:
        """Return activities in [start_date, end_date] with pagination."""
        ...

    @abstractmethod
    async def get_activity_details(self, activity_id: str) -> GarminActivity | None:
        """Return full detail for a single activity."""
        ...

    @abstractmethod
    async def get_daily_summaries(
        self, start_date: date, end_date: date
    ) -> list[GarminDailySummary]:
        """Return daily health summaries for each date in range."""
        ...

    @abstractmethod
    async def get_sleep(
        self, start_date: date, end_date: date
    ) -> list[GarminSleepRecord]:
        """Return sleep records for date range."""
        ...

    @abstractmethod
    async def get_hrv(
        self, start_date: date, end_date: date
    ) -> list[GarminHRVData]:
        """Return HRV data for date range."""
        ...

    @abstractmethod
    async def get_hr_zones(self) -> dict[str, Any]:
        """Return user's configured heart-rate zones."""
        ...

    @abstractmethod
    def get_capabilities(self) -> set[str]:
        """Return set of supported capability strings."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return human-readable provider name."""
        ...


# ─── Exceptions ─────────────────────────────────────────────

class GarminAuthError(Exception):
    """Authentication failed or credentials invalid."""

class GarminRateLimitError(Exception):
    """Rate limit exceeded."""

class GarminAPIError(Exception):
    """Unexpected API error."""

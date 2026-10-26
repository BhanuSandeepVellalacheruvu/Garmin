"""DailyHealthMetric and SleepRecord models."""
from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class DailyHealthMetric(Base, TimestampMixin):
    __tablename__ = "daily_health_metrics"
    __table_args__ = (
        UniqueConstraint("user_id", "calendar_date", name="uq_health_user_date"),
        Index("ix_health_user_date", "user_id", "calendar_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    calendar_date: Mapped[date] = mapped_column(Date, nullable=False)
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_battery_high: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_battery_low: Mapped[int | None] = mapped_column(Integer, nullable=True)
    respiration_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class SleepRecord(Base, TimestampMixin):
    __tablename__ = "sleep_records"
    __table_args__ = (
        UniqueConstraint("user_id", "calendar_date", name="uq_sleep_user_date"),
        Index("ix_sleep_user_date", "user_id", "calendar_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    calendar_date: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sleep_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_sleep_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deep_sleep_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    light_sleep_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rem_sleep_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    awake_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hrv_weekly_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    hrv_last_night: Mapped[float | None] = mapped_column(Float, nullable=True)
    hrv_last_night_5min_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

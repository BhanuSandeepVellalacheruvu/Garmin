"""Live activity tracking session model."""
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class LiveSession(Base, TimestampMixin):
    __tablename__ = "live_sessions"
    __table_args__ = (
        Index("ix_live_session_user_status", "user_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    sport: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")  # active, paused, finished
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    elapsed_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_pace_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elevation_gain_m: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_power: Mapped[int | None] = mapped_column(Integer, nullable=True)
    telemetry_samples: Mapped[list | None] = mapped_column(JSON, nullable=True)  # list of {timestamp, hr, pace, lat, lng, alt}
    emergency_contact_alerted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_ping_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

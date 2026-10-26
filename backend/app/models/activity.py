"""Activity, ActivityLap, ActivitySample models."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, new_uuid


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"
    __table_args__ = (
        UniqueConstraint("garmin_activity_id", name="uq_activity_garmin_id"),
        Index("ix_activity_user_start", "user_id", "start_time"),
        Index("ix_activity_sport", "user_id", "sport_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    garmin_activity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sport_type: Mapped[str] = mapped_column(String(60), nullable=False, default="unknown")
    activity_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation_gain: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    training_effect_aerobic: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_effect_anaerobic: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    laps: Mapped[list["ActivityLap"]] = relationship("ActivityLap", back_populates="activity", cascade="all, delete-orphan")
    samples: Mapped[list["ActivitySample"]] = relationship("ActivitySample", back_populates="activity", cascade="all, delete-orphan")


class ActivityLap(Base):
    __tablename__ = "activity_laps"
    __table_args__ = (Index("ix_lap_activity", "activity_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    activity_id: Mapped[str] = mapped_column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    lap_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elevation_gain: Mapped[float | None] = mapped_column(Float, nullable=True)

    activity: Mapped["Activity"] = relationship("Activity", back_populates="laps")


class ActivitySample(Base):
    __tablename__ = "activity_samples"
    __table_args__ = (Index("ix_sample_activity_time", "activity_id", "timestamp"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    activity_id: Mapped[str] = mapped_column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    activity: Mapped["Activity"] = relationship("Activity", back_populates="samples")

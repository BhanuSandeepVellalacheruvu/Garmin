"""Saved trail and route exploration models."""
from sqlalchemy import String, Float, Boolean, ForeignKey, Index, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class SavedTrail(Base, TimestampMixin):
    __tablename__ = "saved_trails"
    __table_args__ = (
        Index("ix_trail_user_sport", "user_id", "activity_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    elevation_gain_meters: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="moderate")  # easy, moderate, hard, expert
    surface_type: Mapped[str] = mapped_column(String(50), nullable=False, default="trail")  # road, trail, mixed, gravel
    start_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    waypoints_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

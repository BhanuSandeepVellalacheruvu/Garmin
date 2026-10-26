"""UserProfile model."""
from sqlalchemy import String, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default="default")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(60), nullable=False, default="UTC")
    preferred_units: Mapped[str] = mapped_column(String(10), nullable=False, default="metric")
    experience_level: Mapped[str] = mapped_column(String(30), nullable=False, default="intermediate")
    target_race_distance: Mapped[str | None] = mapped_column(String(30), nullable=True)
    target_finish_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_running_days: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weekly_availability_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

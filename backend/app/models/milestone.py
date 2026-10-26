"""Badge and Milestone model for Garmin Connect+ style achievements."""
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class BadgeMilestone(Base, TimestampMixin):
    __tablename__ = "badge_milestones"
    __table_args__ = (
        UniqueConstraint("user_id", "badge_key", name="uq_badge_user_key"),
        Index("ix_badge_user_category", "user_id", "category"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    badge_key: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="running")  # running, consistency, distance, elevation, recovery
    tier: Mapped[str] = mapped_column(String(30), nullable=False, default="bronze")  # bronze, silver, gold, platinum
    icon: Mapped[str] = mapped_column(String(50), nullable=False, default="award")
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_unlocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

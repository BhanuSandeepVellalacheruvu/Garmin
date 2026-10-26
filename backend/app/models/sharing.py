"""LiveTrack and Activity Share Link models."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class ActivityShareLink(Base, TimestampMixin):
    __tablename__ = "activity_share_links"
    __table_args__ = (
        UniqueConstraint("access_token", name="uq_share_link_token"),
        Index("ix_share_user_activity", "user_id", "activity_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    activity_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=True)
    access_token: Mapped[str] = mapped_column(String(64), nullable=False, default=new_uuid)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    include_gps: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    include_hr: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    include_splits: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

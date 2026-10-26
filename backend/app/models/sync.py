"""SyncJob and ProviderCredential models."""
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class SyncJob(Base, TimestampMixin):
    __tablename__ = "sync_jobs"
    __table_args__ = (Index("ix_sync_user_status", "user_id", "status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="official")
    job_type: Mapped[str] = mapped_column(String(20), nullable=False, default="incremental")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_synced: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_activity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_synced_date: Mapped[str | None] = mapped_column(String(20), nullable=True)


class ProviderCredential(Base, TimestampMixin):
    """Stores encrypted access tokens. The encryption key is derived from APP_SECRET_KEY."""
    __tablename__ = "provider_credentials"
    __table_args__ = (Index("ix_cred_user_provider", "user_id", "provider"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    # Token stored encrypted via Fernet(sha256(APP_SECRET_KEY))
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

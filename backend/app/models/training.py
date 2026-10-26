"""Training-related models: RaceGoal, PersonalRecord, TrainingPlan, TrainingPlanDay."""
from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, new_uuid


class RaceGoal(Base, TimestampMixin):
    __tablename__ = "race_goals"
    __table_args__ = (Index("ix_race_goal_user", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    race_name: Mapped[str] = mapped_column(String(255), nullable=False)
    race_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PersonalRecord(Base, TimestampMixin):
    __tablename__ = "personal_records"
    __table_args__ = (Index("ix_pr_user", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    activity_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)
    record_type: Mapped[str] = mapped_column(String(60), nullable=False)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class TrainingPlan(Base, TimestampMixin):
    __tablename__ = "training_plans"
    __table_args__ = (Index("ix_plan_user", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    race_goal_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("race_goals.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_by: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    days: Mapped[list["TrainingPlanDay"]] = relationship("TrainingPlanDay", back_populates="plan", cascade="all, delete-orphan")


class TrainingPlanDay(Base):
    __tablename__ = "training_plan_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    workout_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_pace_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan: Mapped["TrainingPlan"] = relationship("TrainingPlan", back_populates="days")

"""Nutrition and hydration models."""
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, new_uuid


class NutritionEntry(Base, TimestampMixin):
    __tablename__ = "nutrition_entries"
    __table_args__ = (
        Index("ix_nutrition_user_date", "user_id", "entry_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False, default="snack")  # breakfast, lunch, dinner, snack, hydration
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    water_ml: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class NutritionTarget(Base, TimestampMixin):
    __tablename__ = "nutrition_targets"
    __table_args__ = (
        Index("ix_nutrition_target_user", "user_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    target_calories: Mapped[float] = mapped_column(Float, nullable=False, default=2200.0)
    target_protein_g: Mapped[float] = mapped_column(Float, nullable=False, default=140.0)
    target_carbs_g: Mapped[float] = mapped_column(Float, nullable=False, default=250.0)
    target_fat_g: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    target_water_ml: Mapped[float] = mapped_column(Float, nullable=False, default=2500.0)
    active_from: Mapped[date] = mapped_column(Date, nullable=False)

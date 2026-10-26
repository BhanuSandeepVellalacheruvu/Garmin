"""Nutrition and hydration tracking endpoints."""
from datetime import date, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.nutrition import NutritionEntry, NutritionTarget
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


class NutritionEntryCreate(BaseModel):
    entry_date: date
    meal_type: str = "snack"  # breakfast, lunch, dinner, snack, hydration
    food_name: str
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    water_ml: float = 0.0
    notes: str | None = None


class NutritionTargetCreate(BaseModel):
    target_calories: float = 2200.0
    target_protein_g: float = 140.0
    target_carbs_g: float = 250.0
    target_fat_g: float = 70.0
    target_water_ml: float = 2500.0


@router.get("/entries")
async def get_entries(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=7)

    query = (
        select(NutritionEntry)
        .where(
            and_(
                NutritionEntry.user_id == user.id,
                NutritionEntry.entry_date >= start_date,
                NutritionEntry.entry_date <= end_date,
            )
        )
        .order_by(desc(NutritionEntry.entry_date), desc(NutritionEntry.created_at))
    )
    result = await db.execute(query)
    entries = result.scalars().all()

    return [
        {
            "id": e.id,
            "entry_date": e.entry_date.isoformat(),
            "meal_type": e.meal_type,
            "food_name": e.food_name,
            "calories": round(e.calories, 1),
            "protein_g": round(e.protein_g, 1),
            "carbs_g": round(e.carbs_g, 1),
            "fat_g": round(e.fat_g, 1),
            "water_ml": round(e.water_ml, 1),
            "notes": e.notes,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]


@router.post("/entries")
async def create_entry(
    payload: NutritionEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    entry = NutritionEntry(
        id=new_uuid(),
        user_id=user.id,
        entry_date=payload.entry_date,
        meal_type=payload.meal_type,
        food_name=payload.food_name,
        calories=payload.calories,
        protein_g=payload.protein_g,
        carbs_g=payload.carbs_g,
        fat_g=payload.fat_g,
        water_ml=payload.water_ml,
        notes=payload.notes,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {"id": entry.id, "status": "created"}


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    result = await db.execute(
        select(NutritionEntry).where(
            and_(NutritionEntry.id == entry_id, NutritionEntry.user_id == user.id)
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    await db.delete(entry)
    await db.commit()
    return {"status": "deleted"}


@router.get("/target")
async def get_target(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    result = await db.execute(
        select(NutritionTarget)
        .where(NutritionTarget.user_id == user.id)
        .order_by(desc(NutritionTarget.active_from))
        .limit(1)
    )
    target = result.scalar_one_or_none()
    if not target:
        # Return sensible defaults
        return {
            "target_calories": 2200.0,
            "target_protein_g": 140.0,
            "target_carbs_g": 250.0,
            "target_fat_g": 70.0,
            "target_water_ml": 2500.0,
            "active_from": date.today().isoformat(),
        }
    return {
        "id": target.id,
        "target_calories": target.target_calories,
        "target_protein_g": target.target_protein_g,
        "target_carbs_g": target.target_carbs_g,
        "target_fat_g": target.target_fat_g,
        "target_water_ml": target.target_water_ml,
        "active_from": target.active_from.isoformat(),
    }


@router.post("/target")
async def update_target(
    payload: NutritionTargetCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    target = NutritionTarget(
        id=new_uuid(),
        user_id=user.id,
        target_calories=payload.target_calories,
        target_protein_g=payload.target_protein_g,
        target_carbs_g=payload.target_carbs_g,
        target_fat_g=payload.target_fat_g,
        target_water_ml=payload.target_water_ml,
        active_from=date.today(),
    )
    db.add(target)
    await db.commit()
    return {"status": "updated", "id": target.id}


@router.get("/summary")
async def get_summary(
    days: int = Query(default=14, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Provides daily time-series data for each individual nutrition and hydration chart."""
    user = await _user(db)
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 1. Fetch target
    target_res = await db.execute(
        select(NutritionTarget)
        .where(NutritionTarget.user_id == user.id)
        .order_by(desc(NutritionTarget.active_from))
        .limit(1)
    )
    target = target_res.scalar_one_or_none()
    target_cal = target.target_calories if target else 2200.0
    target_water = target.target_water_ml if target else 2500.0
    target_protein = target.target_protein_g if target else 140.0
    target_carbs = target.target_carbs_g if target else 250.0
    target_fat = target.target_fat_g if target else 70.0

    # 2. Fetch all entries in window
    entries_res = await db.execute(
        select(NutritionEntry).where(
            and_(
                NutritionEntry.user_id == user.id,
                NutritionEntry.entry_date >= start_date,
                NutritionEntry.entry_date <= end_date,
            )
        )
    )
    entries = entries_res.scalars().all()

    # Aggregate by date
    daily_map: dict[str, dict[str, float]] = {}
    cur = start_date
    while cur <= end_date:
        d_str = cur.isoformat()
        daily_map[d_str] = {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "water_ml": 0.0,
        }
        cur += timedelta(days=1)

    for e in entries:
        d_str = e.entry_date.isoformat()
        if d_str in daily_map:
            daily_map[d_str]["calories"] += e.calories
            daily_map[d_str]["protein_g"] += e.protein_g
            daily_map[d_str]["carbs_g"] += e.carbs_g
            daily_map[d_str]["fat_g"] += e.fat_g
            daily_map[d_str]["water_ml"] += e.water_ml

    time_series = []
    for d_str, vals in sorted(daily_map.items()):
        cal = round(vals["calories"], 1)
        water = round(vals["water_ml"], 1)
        prot = round(vals["protein_g"], 1)
        carb = round(vals["carbs_g"], 1)
        fat = round(vals["fat_g"], 1)
        time_series.append({
            "date": d_str,
            "calories": cal,
            "target_calories": target_cal,
            "calories_pct": round((cal / target_cal * 100), 1) if target_cal > 0 else 0,
            "water_ml": water,
            "target_water_ml": target_water,
            "water_pct": round((water / target_water * 100), 1) if target_water > 0 else 0,
            "protein_g": prot,
            "target_protein_g": target_protein,
            "carbs_g": carb,
            "target_carbs_g": target_carbs,
            "fat_g": fat,
            "target_fat_g": target_fat,
        })

    return {
        "targets": {
            "calories": target_cal,
            "water_ml": target_water,
            "protein_g": target_protein,
            "carbs_g": target_carbs,
            "fat_g": target_fat,
        },
        "days": time_series,
    }

"""Training calendar, plans, and race goals endpoints."""
from datetime import date, datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.training import RaceGoal, TrainingPlan, TrainingPlanDay, PersonalRecord
from app.models.activity import Activity
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


class RaceGoalCreate(BaseModel):
    race_name: str
    race_date: date | None = None
    distance_meters: float | None = None
    target_time_seconds: int | None = None
    notes: str | None = None


class TrainingPlanCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    race_goal_id: str | None = None


@router.get("/calendar")
async def get_calendar(
    year: int = Query(default=date.today().year),
    month: int = Query(default=date.today().month),
    db: AsyncSession = Depends(get_db),
):
    user = await _user(db)
    start_month = date(year, month, 1)
    if month == 12:
        end_month = date(year + 1, 1, 1)
    else:
        end_month = date(year, month + 1, 1)

    # 1. Activities in this month
    act_r = await db.execute(
        select(Activity).where(
            and_(
                Activity.user_id == user.id,
                Activity.start_time >= start_month,
                Activity.start_time < end_month,
            )
        )
    )
    acts = act_r.scalars().all()

    # 2. Planned training sessions
    plan_days_r = await db.execute(
        select(TrainingPlanDay).where(
            and_(TrainingPlanDay.date >= start_month, TrainingPlanDay.date < end_month)
        )
    )
    plan_days = plan_days_r.scalars().all()

    # 3. Race goals in this month
    goals_r = await db.execute(
        select(RaceGoal).where(
            and_(
                RaceGoal.user_id == user.id,
                RaceGoal.race_date >= start_month,
                RaceGoal.race_date < end_month,
            )
        )
    )
    goals = goals_r.scalars().all()

    return {
        "year": year,
        "month": month,
        "activities": [
            {
                "id": a.id,
                "date": a.start_time.strftime("%Y-%m-%d"),
                "name": a.name,
                "sport_type": a.sport_type,
                "distance_km": round(a.distance_meters / 1000, 2) if a.distance_meters else None,
                "duration_s": a.duration_seconds,
            }
            for a in acts
        ],
        "planned_days": [
            {
                "id": p.id,
                "date": p.date.isoformat(),
                "workout_type": p.workout_type,
                "description": p.description,
                "target_distance_km": round(p.target_distance_meters / 1000, 2)
                if p.target_distance_meters
                else None,
                "completed": p.completed,
            }
            for p in plan_days
        ],
        "goals": [
            {
                "id": g.id,
                "name": g.race_name,
                "date": g.race_date.isoformat() if g.race_date else None,
                "distance_km": round(g.distance_meters / 1000, 2) if g.distance_meters else None,
            }
            for g in goals
        ],
    }


@router.get("/goals")
async def list_goals(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    r = await db.execute(select(RaceGoal).where(RaceGoal.user_id == user.id).order_by(RaceGoal.race_date))
    goals = r.scalars().all()
    return [
        {
            "id": g.id,
            "race_name": g.race_name,
            "race_date": g.race_date.isoformat() if g.race_date else None,
            "distance_meters": g.distance_meters,
            "target_time_seconds": g.target_time_seconds,
            "status": g.status,
            "notes": g.notes,
        }
        for g in goals
    ]


@router.post("/goals")
async def create_goal(req: RaceGoalCreate, db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    goal = RaceGoal(
        id=new_uuid(),
        user_id=user.id,
        race_name=req.race_name,
        race_date=req.race_date,
        distance_meters=req.distance_meters,
        target_time_seconds=req.target_time_seconds,
        notes=req.notes,
        status="active",
    )
    db.add(goal)
    await db.commit()
    return {"id": goal.id, "status": "created"}


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    r = await db.execute(
        select(TrainingPlan).where(TrainingPlan.user_id == user.id).order_by(desc(TrainingPlan.start_date))
    )
    plans = r.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "status": p.status,
            "created_by": p.created_by,
        }
        for p in plans
    ]


@router.post("/plans")
async def create_plan(req: TrainingPlanCreate, db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    plan = TrainingPlan(
        id=new_uuid(),
        user_id=user.id,
        name=req.name,
        start_date=req.start_date,
        end_date=req.end_date,
        race_goal_id=req.race_goal_id,
        status="active",
        created_by="user",
        approved_at=datetime.now(timezone.utc),
    )
    db.add(plan)
    await db.commit()
    return {"id": plan.id, "status": "created"}

"""Garmin Connect+ inspired Badges and Milestones endpoints."""
from datetime import datetime, timezone, timedelta
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.milestone import BadgeMilestone
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.user import UserProfile
from app.models.base import new_uuid

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


DEFAULT_BADGES = [
    {
        "badge_key": "run_5k",
        "title": "5K Finisher",
        "description": "Completed a run of at least 5 kilometers.",
        "category": "running",
        "tier": "bronze",
        "icon": "trophy",
    },
    {
        "badge_key": "run_10k",
        "title": "10K Crusher",
        "description": "Completed a run of at least 10 kilometers.",
        "category": "running",
        "tier": "silver",
        "icon": "medal",
    },
    {
        "badge_key": "run_half",
        "title": "Half Marathon Finisher",
        "description": "Completed a 21.1 kilometer half marathon distance.",
        "category": "running",
        "tier": "gold",
        "icon": "award",
    },
    {
        "badge_key": "total_dist_50k",
        "title": "50K Distance Club",
        "description": "Logged over 50 kilometers in total lifetime activities.",
        "category": "distance",
        "tier": "bronze",
        "icon": "navigation",
    },
    {
        "badge_key": "total_dist_100k",
        "title": "Century Runner",
        "description": "Logged over 100 kilometers in total lifetime activities.",
        "category": "distance",
        "tier": "silver",
        "icon": "compass",
    },
    {
        "badge_key": "elevation_climber",
        "title": "Hill Climber",
        "description": "Conquered over 100 meters of elevation gain in a single workout.",
        "category": "elevation",
        "tier": "bronze",
        "icon": "mountain",
    },
    {
        "badge_key": "early_bird",
        "title": "Early Bird Runner",
        "description": "Started and completed a workout before 8:00 AM.",
        "category": "consistency",
        "tier": "bronze",
        "icon": "sunrise",
    },
    {
        "badge_key": "sleep_champion",
        "title": "Sleep Champion",
        "description": "Achieved a Garmin sleep score of 80 or higher with 7+ hours duration.",
        "category": "recovery",
        "tier": "gold",
        "icon": "moon",
    },
    {
        "badge_key": "hrv_balanced",
        "title": "Balanced Recovery",
        "description": "Maintained a balanced overnight HRV baseline.",
        "category": "recovery",
        "tier": "silver",
        "icon": "heart-pulse",
    },
    {
        "badge_key": "workout_streak",
        "title": "Triple Play Streak",
        "description": "Logged activities across at least 3 distinct days in a single week.",
        "category": "consistency",
        "tier": "silver",
        "icon": "flame",
    },
]


@router.get("")
async def get_badges(db: AsyncSession = Depends(get_db)):
    """Returns all badges with current unlock status and progress."""
    user = await _user(db)

    # 1. Fetch user's saved badge records
    res = await db.execute(
        select(BadgeMilestone).where(BadgeMilestone.user_id == user.id)
    )
    user_badges = {b.badge_key: b for b in res.scalars().all()}

    # Merge with catalog
    badge_list = []
    for meta in DEFAULT_BADGES:
        key = meta["badge_key"]
        ub = user_badges.get(key)
        badge_list.append({
            "key": key,
            "title": meta["title"],
            "description": meta["description"],
            "category": meta["category"],
            "tier": meta["tier"],
            "icon": meta["icon"],
            "is_unlocked": ub.is_unlocked if ub else False,
            "achieved_at": ub.achieved_at.isoformat() if (ub and ub.achieved_at) else None,
            "metric_value": ub.metric_value if ub else None,
        })

    # Summary counts
    total_unlocked = sum(1 for b in badge_list if b["is_unlocked"])
    return {
        "total_badges": len(badge_list),
        "unlocked_count": total_unlocked,
        "completion_pct": round((total_unlocked / len(badge_list) * 100), 1) if badge_list else 0,
        "badges": badge_list,
    }


@router.post("/evaluate")
async def evaluate_badges(db: AsyncSession = Depends(get_db)):
    """Evaluates user's actual database records and awards all eligible badges."""
    user = await _user(db)

    # Fetch user's activities
    act_res = await db.execute(select(Activity).where(Activity.user_id == user.id))
    activities = act_res.scalars().all()

    # Fetch sleep records
    sleep_res = await db.execute(select(SleepRecord).where(SleepRecord.user_id == user.id))
    sleep_records = sleep_res.scalars().all()

    # Fetch health metrics
    health_res = await db.execute(select(DailyHealthMetric).where(DailyHealthMetric.user_id == user.id))
    health_metrics = health_res.scalars().all()

    # Fetch existing badges
    existing_res = await db.execute(select(BadgeMilestone).where(BadgeMilestone.user_id == user.id))
    existing_map = {b.badge_key: b for b in existing_res.scalars().all()}

    newly_unlocked = []

    # Criteria checks:
    total_distance_m = sum((a.distance_meters or 0) for a in activities)
    max_single_dist = max([(a.distance_meters or 0) for a in activities] or [0])
    max_elevation = max([(a.elevation_gain or 0) for a in activities] or [0])
    has_early_run = any(a.start_time.hour < 8 for a in activities)
    has_good_sleep = any((s.sleep_score or 0) >= 80 and (s.total_sleep_seconds or 0) >= 25200 for s in sleep_records)
    has_balanced_hrv = any(s.hrv_last_night and s.hrv_last_night >= 40 for s in sleep_records)

    evaluations = {
        "run_5k": (max_single_dist >= 5000, max_single_dist),
        "run_10k": (max_single_dist >= 10000, max_single_dist),
        "run_half": (max_single_dist >= 21000, max_single_dist),
        "total_dist_50k": (total_distance_m >= 50000, total_distance_m),
        "total_dist_100k": (total_distance_m >= 100000, total_distance_m),
        "elevation_climber": (max_elevation >= 100, max_elevation),
        "early_bird": (has_early_run, 1.0 if has_early_run else 0.0),
        "sleep_champion": (has_good_sleep, 85.0 if has_good_sleep else 0.0),
        "hrv_balanced": (has_balanced_hrv, 1.0 if has_balanced_hrv else 0.0),
        "workout_streak": (len(activities) >= 3, float(len(activities))),
    }

    meta_lookup = {b["badge_key"]: b for b in DEFAULT_BADGES}

    for key, (earned, metric_val) in evaluations.items():
        if not earned:
            continue
        meta = meta_lookup.get(key)
        if not meta:
            continue

        existing = existing_map.get(key)
        if not existing:
            nb = BadgeMilestone(
                id=new_uuid(),
                user_id=user.id,
                badge_key=key,
                title=meta["title"],
                description=meta["description"],
                category=meta["category"],
                tier=meta["tier"],
                icon=meta["icon"],
                achieved_at=datetime.now(timezone.utc),
                metric_value=metric_val,
                is_unlocked=True,
            )
            db.add(nb)
            newly_unlocked.append(meta["title"])
        elif not existing.is_unlocked:
            existing.is_unlocked = True
            existing.achieved_at = datetime.now(timezone.utc)
            existing.metric_value = metric_val
            newly_unlocked.append(meta["title"])

    await db.commit()

    return {
        "evaluated_count": len(DEFAULT_BADGES),
        "newly_unlocked": newly_unlocked,
    }

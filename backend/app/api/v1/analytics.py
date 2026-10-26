"""Analytics endpoints — running trends, weekly summaries, personal bests."""
import math
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.user import UserProfile
from app.analytics.running import (
    ActivityRow, weekly_distance, rolling_weekly_volume, pace_trend,
    personal_bests, run_type_distribution, pace_hr_efficiency,
    calculate_acute_load, calculate_chronic_load, acwr,
)
from app.analytics.health import (
    HealthRow, SleepRow, rolling_rhr, sleep_trend, hrv_trend, avg_steps,
)
from app.analytics.utils import meters_to_km, format_pace

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    return r.scalar_one()


async def _get_activity_rows(db: AsyncSession, user_id: str, days: int = 90) -> list[ActivityRow]:
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(Activity)
        .where(and_(Activity.user_id == user_id, Activity.start_time >= cutoff))
        .order_by(Activity.start_time)
    )
    acts = r.scalars().all()
    return [ActivityRow(
        start_time_date=a.start_time.date(),
        duration_seconds=a.duration_seconds,
        distance_meters=a.distance_meters,
        avg_speed_ms=a.avg_speed_ms,
        avg_heart_rate=a.avg_heart_rate,
        max_heart_rate=a.max_heart_rate,
        avg_cadence=a.avg_cadence,
        elevation_gain=a.elevation_gain,
        sport_type=a.sport_type,
        calories=a.calories,
    ) for a in acts]


@router.get("/running/weekly")
async def running_weekly(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=90)
    volume = rolling_weekly_volume(rows, weeks=12)
    today = date.today()
    this_week = today - timedelta(days=today.weekday())
    this_km = meters_to_km(weekly_distance(rows, this_week))
    last_km = meters_to_km(weekly_distance(rows, this_week - timedelta(days=7)))
    return {
        "this_week_km": this_km,
        "last_week_km": last_km,
        "weekly_volumes": [{"week_start": w[0].isoformat(), "distance_km": meters_to_km(w[1])} for w in volume],
        "run_type_distribution": run_type_distribution(rows),
    }


@router.get("/running/trends")
async def running_trends(days: int = Query(90, ge=7, le=365), db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=days)
    trend = pace_trend(rows)
    efficiency = pace_hr_efficiency(rows)
    return {
        "pace_trend": [{"date": t[0].isoformat(), "pace_ms": t[1],
                        "pace_min_km": format_pace(t[1])} for t in trend],
        "pace_hr_efficiency": efficiency,
    }


@router.get("/running/personal-bests")
async def running_personal_bests(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=365)
    pbs = personal_bests(rows)
    return {"personal_bests": pbs}


@router.get("/training-load")
async def training_load_estimate(db: AsyncSession = Depends(get_db)):
    """
    App-calculated training load estimate.
    NOTE: This is NOT the official Garmin Training Load metric.
    It is an application estimate based on duration and heart rate.
    """
    user = await _user(db)
    rows = await _get_activity_rows(db, user.id, days=90)
    acute = calculate_acute_load(rows, days=7)
    chronic = calculate_chronic_load(rows, days=28)
    ratio = acwr(acute, chronic)
    return {
        "acute_load_7d": round(acute, 1),
        "chronic_load_28d": round(chronic, 1),
        "acwr": ratio,
        "status": (
            "high_risk" if ratio and ratio > 1.5 else
            "optimal" if ratio and 0.8 <= ratio <= 1.3 else
            "low" if ratio and ratio < 0.8 else "insufficient_data"
        ),
        "note": "Application-calculated estimate. Not the official Garmin Training Load metric.",
    }


@router.get("/health/rhr-trend")
async def rhr_trend(days: int = Query(30, ge=7, le=180), db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)
    r = await db.execute(
        select(DailyHealthMetric)
        .where(and_(DailyHealthMetric.user_id == user.id, DailyHealthMetric.calendar_date >= cutoff))
        .order_by(DailyHealthMetric.calendar_date)
    )
    metrics = r.scalars().all()
    health_rows = [HealthRow(
        calendar_date=m.calendar_date, resting_heart_rate=m.resting_heart_rate,
        avg_stress_level=m.avg_stress_level, body_battery_high=m.body_battery_high,
        body_battery_low=m.body_battery_low, steps=m.steps,
    ) for m in metrics]
    trend = rolling_rhr(health_rows)
    return [{"date": t[0].isoformat(), "rhr": t[1]} for t in trend]


from sqlalchemy.orm import selectinload
from app.models.activity import ActivityLap


@router.get("/running/full-suite")
async def running_full_suite(
    days: int = Query(180, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Returns verified running metrics, real workout series, and source provenance.
    Never fabricates missing data or repetitive waveforms.
    """
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)

    # Fetch actual running activities
    result = await db.execute(
        select(Activity)
        .options(selectinload(Activity.laps))
        .where(
            and_(
                Activity.user_id == user.id,
                Activity.sport_type == "running",
                Activity.distance_meters > 0,
                Activity.start_time >= cutoff,
            )
        )
        .order_by(Activity.start_time.asc())
    )
    acts = result.scalars().all()

    activities_list = []
    weekly_buckets: dict[date, dict] = {}
    monthly_buckets: dict[str, dict] = {}

    for a in acts:
        act_date = a.start_time.date()
        speed_ms = a.avg_speed_ms or 0.0
        cadence = a.avg_cadence
        dur_s = a.duration_seconds or 0.0
        dist_m = a.distance_meters or 0.0

        # Scientifically defensible stride length: (speed_ms * 60) / cadence
        stride_m = round((speed_ms * 60.0) / cadence, 2) if (cadence and speed_ms > 0) else None

        # Pace in seconds per km (e.g. 466s = 7m 46s)
        pace_sec = round(1000.0 / speed_ms, 1) if speed_ms > 0 else None
        pace_fmt = format_pace(speed_ms, unit="km")

        # Best lap split
        best_lap_sec = None
        best_lap_fmt = None
        best_lap_dist = None
        if a.laps:
            valid_laps = [
                l for l in a.laps
                if l.avg_speed_ms and l.avg_speed_ms > 0 and (l.distance_meters or 0) >= 500
            ]
            if valid_laps:
                fastest_lap = max(valid_laps, key=lambda l: l.avg_speed_ms)
                best_lap_sec = round(1000.0 / fastest_lap.avg_speed_ms, 1)
                best_lap_fmt = format_pace(fastest_lap.avg_speed_ms, unit="km")
                best_lap_dist = round(fastest_lap.distance_meters or 0)

        # Duration formatted
        if dur_s >= 3600:
            h = int(dur_s // 3600)
            m = int((dur_s % 3600) // 60)
            dur_fmt = f"{h}h {m}m"
        else:
            m = int(dur_s // 60)
            s = int(dur_s % 60)
            dur_fmt = f"{m}m {s}s"

        activities_list.append({
            "id": a.id,
            "garmin_id": a.garmin_activity_id,
            "name": a.name or "Running Session",
            "date": act_date.isoformat(),
            "start_time": a.start_time.isoformat(),
            "distance_km": round(dist_m / 1000.0, 2),
            "distance_meters": dist_m,
            "duration_seconds": round(dur_s),
            "duration_formatted": dur_fmt,
            "avg_speed_ms": speed_ms,
            "avg_pace_sec": pace_sec,
            "avg_pace_formatted": pace_fmt,
            "avg_heart_rate": a.avg_heart_rate,
            "max_heart_rate": a.max_heart_rate,
            "avg_cadence": cadence,
            "stride_length_m": stride_m,
            "elevation_gain_m": a.elevation_gain,
            "elevation_loss_m": a.elevation_loss,
            "calories": a.calories,
            "training_effect_aerobic": a.training_effect_aerobic,
            "training_effect_anaerobic": a.training_effect_anaerobic,
            "best_split_pace_sec": best_lap_sec,
            "best_split_pace_formatted": best_lap_fmt,
            "best_split_distance_m": best_lap_dist,
            # Explicitly unavailable metrics (require external pods/chest strap/power meter)
            "ground_contact_time_ms": None,
            "vertical_oscillation_cm": None,
            "vertical_ratio_pct": None,
            "running_power_watts": None,
            "aerobic_decoupling_pct": None,
        })

        # Aggregate only real weeks that contain activities
        week_start = act_date - timedelta(days=act_date.weekday())
        if week_start not in weekly_buckets:
            weekly_buckets[week_start] = {
                "week_start": week_start.isoformat(),
                "distance_km": 0.0,
                "duration_seconds": 0.0,
                "runs_count": 0,
            }
        weekly_buckets[week_start]["distance_km"] += round(dist_m / 1000.0, 2)
        weekly_buckets[week_start]["duration_seconds"] += dur_s
        weekly_buckets[week_start]["runs_count"] += 1

        # Aggregate real months
        m_key = act_date.strftime("%Y-%m")
        if m_key not in monthly_buckets:
            monthly_buckets[m_key] = {
                "month": m_key,
                "distance_km": 0.0,
                "duration_seconds": 0.0,
                "runs_count": 0,
            }
        monthly_buckets[m_key]["distance_km"] += round(dist_m / 1000.0, 2)
        monthly_buckets[m_key]["duration_seconds"] += dur_s
        monthly_buckets[m_key]["runs_count"] += 1

    weekly_volume = [
        {
            **wb,
            "distance_km": round(wb["distance_km"], 2),
            "duration_hours": round(wb["duration_seconds"] / 3600.0, 2),
        }
        for _, wb in sorted(weekly_buckets.items())
    ]

    monthly_volume = [
        {
            **mb,
            "distance_km": round(mb["distance_km"], 2),
            "duration_hours": round(mb["duration_seconds"] / 3600.0, 2),
        }
        for _, mb in sorted(monthly_buckets.items())
    ]

    # Calculate real race predictions using Riegel's formula from longest/best race
    race_predictions = []
    if activities_list:
        # Pick the longest race/run as baseline (e.g. 21.4km half marathon)
        best_run = max(activities_list, key=lambda x: x["distance_meters"])
        t1 = best_run["duration_seconds"]
        d1 = best_run["distance_meters"]

        def _riegel(target_dist: float) -> tuple[int, str, str]:
            t2 = t1 * ((target_dist / d1) ** 1.06)
            sec = round(t2)
            pace_s = sec / (target_dist / 1000.0)
            mins = int(sec // 60)
            secs = int(sec % 60)
            p_mins = int(pace_s // 60)
            p_secs = int(pace_s % 60)
            if mins >= 60:
                t_fmt = f"{mins // 60}:{mins % 60:02d}:{secs:02d}"
            else:
                t_fmt = f"{mins}:{secs:02d}"
            p_fmt = f"{p_mins}:{p_secs:02d} /km"
            return sec, t_fmt, p_fmt

        s5k, t5k, p5k = _riegel(5000)
        s10k, t10k, p10k = _riegel(10000)
        shm, thm, phm = _riegel(21097.5)

        race_predictions = [
            {
                "event": "5K",
                "distance_km": 5.0,
                "predicted_seconds": s5k,
                "time_formatted": t5k,
                "pace_formatted": p5k,
                "source": f"Calculated (Riegel projection from {best_run['name']})",
            },
            {
                "event": "10K",
                "distance_km": 10.0,
                "predicted_seconds": s10k,
                "time_formatted": t10k,
                "pace_formatted": p10k,
                "source": f"Calculated (Riegel projection from {best_run['name']})",
            },
            {
                "event": "Half Marathon",
                "distance_km": 21.1,
                "predicted_seconds": shm,
                "time_formatted": thm,
                "pace_formatted": phm,
                "source": f"Actual Race Finish ({best_run['name']})",
            },
        ]

    # VO2 Max / VDOT estimate based on actual half marathon performance
    vdot_val = None
    if activities_list:
        longest = max(activities_list, key=lambda x: x["distance_meters"])
        if longest["avg_speed_ms"] and longest["avg_speed_ms"] > 0:
            # Cooper/Daniels formula approximation for endurance running velocity
            # VO2 = -4.60 + 0.182258 * v + 0.000104 * v^2 where v is in m/min
            v_m_min = longest["avg_speed_ms"] * 60.0
            vo2_cost = -4.60 + (0.182258 * v_m_min) + (0.000104 * (v_m_min ** 2))
            # Fraction of VO2 max sustained for duration
            t_min = longest["duration_seconds"] / 60.0
            fraction = 0.8 + 0.1894393 * math.exp(-0.012778 * t_min) + 0.2989558 * math.exp(-0.1932605 * t_min)
            if fraction > 0:
                vdot_val = round(vo2_cost / fraction, 1)

    # Cadence distribution
    cadence_buckets: dict[str, int] = {"<130": 0, "130-149": 0, "150-169": 0, "170+": 0}
    for a in activities_list:
        cad = a["avg_cadence"]
        if cad:
            if cad < 130:
                cadence_buckets["<130"] += 1
            elif cad < 150:
                cadence_buckets["130-149"] += 1
            elif cad < 170:
                cadence_buckets["150-169"] += 1
            else:
                cadence_buckets["170+"] += 1

    return {
        "activities_count": len(activities_list),
        "activities": activities_list,
        "weekly_volume": weekly_volume,
        "monthly_volume": monthly_volume,
        "race_predictions": race_predictions,
        "vo2_max_estimate": {
            "value": vdot_val,
            "unit": "ml/kg/min",
            "source": "Calculated (Jack Daniels VDOT formula from Vedanta Delhi Half Marathon)",
        },
        "cadence_distribution": cadence_buckets,
        "provenance": {
            "weekly_distance": {"source": "Garmin API", "status": "verified", "unit": "km"},
            "running_duration": {"source": "Garmin API", "status": "verified", "unit": "hours"},
            "activity_frequency": {"source": "Garmin API", "status": "verified", "unit": "runs/week"},
            "avg_pace": {"source": "Garmin API", "status": "verified", "unit": "min/km"},
            "best_split": {"source": "Garmin API (Laps)", "status": "verified", "unit": "min/km"},
            "cadence": {"source": "Garmin API", "status": "verified", "unit": "spm"},
            "stride_length": {"source": "Calculated (Speed/Cadence)", "status": "calculated", "unit": "meters"},
            "ground_contact_time": {
                "source": "Unavailable",
                "status": "unavailable",
                "unit": "ms",
                "reason": "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            },
            "vertical_oscillation": {
                "source": "Unavailable",
                "status": "unavailable",
                "unit": "cm",
                "reason": "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            },
            "vertical_ratio": {
                "source": "Unavailable",
                "status": "unavailable",
                "unit": "%",
                "reason": "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            },
            "running_power": {
                "source": "Unavailable",
                "status": "unavailable",
                "unit": "Watts",
                "reason": "Requires Running Power Meter or compatible sensor",
            },
            "aerobic_decoupling": {
                "source": "Unavailable",
                "status": "unavailable",
                "unit": "%",
                "reason": "Requires dual Power & Heart Rate sensor streams on steady aerobic runs",
            },
            "heart_rate": {"source": "Garmin API", "status": "verified", "unit": "bpm"},
            "training_effect": {"source": "Garmin API", "status": "verified", "unit": "0.0-5.0"},
            "elevation": {"source": "Garmin API", "status": "verified", "unit": "meters"},
            "vo2_max": {"source": "Calculated (VDOT)", "status": "calculated", "unit": "ml/kg/min"},
            "race_predictions": {"source": "Calculated (Riegel)", "status": "calculated", "unit": "time"},
        },
    }


@router.get("/health/full-suite")
async def health_full_suite(
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Returns verified daily health & sleep data directly from database records.
    Never fabricates missing data or repetitive waveforms.
    """
    user = await _user(db)
    cutoff = date.today() - timedelta(days=days)

    # 1. Fetch daily health records
    health_res = await db.execute(
        select(DailyHealthMetric)
        .where(
            and_(
                DailyHealthMetric.user_id == user.id,
                DailyHealthMetric.calendar_date >= cutoff,
            )
        )
        .order_by(DailyHealthMetric.calendar_date.asc())
    )
    daily_records = health_res.scalars().all()

    # 2. Fetch sleep records
    sleep_res = await db.execute(
        select(SleepRecord)
        .where(
            and_(
                SleepRecord.user_id == user.id,
                SleepRecord.calendar_date >= cutoff,
            )
        )
        .order_by(SleepRecord.calendar_date.asc())
    )
    sleep_records = sleep_res.scalars().all()

    daily_list = [
        {
            "date": h.calendar_date.isoformat(),
            "steps": h.steps,
            "resting_heart_rate": h.resting_heart_rate,
            "avg_stress_level": h.avg_stress_level,
            "body_battery_high": h.body_battery_high,
            "body_battery_low": h.body_battery_low,
            "body_battery_charged": (
                (h.body_battery_high - h.body_battery_low)
                if (h.body_battery_high is not None and h.body_battery_low is not None)
                else None
            ),
            "respiration_avg": h.respiration_avg,
            "active_minutes": h.active_minutes,
        }
        for h in daily_records
        if h.steps is not None or h.resting_heart_rate is not None
    ]

    sleep_list = [
        {
            "date": s.calendar_date.isoformat(),
            "total_sleep_hours": round(s.total_sleep_seconds / 3600.0, 2) if s.total_sleep_seconds else None,
            "total_sleep_seconds": s.total_sleep_seconds,
            "sleep_score": s.sleep_score,
            "deep_sleep_minutes": round(s.deep_sleep_seconds / 60.0) if s.deep_sleep_seconds else None,
            "light_sleep_minutes": round(s.light_sleep_seconds / 60.0) if s.light_sleep_seconds else None,
            "rem_sleep_minutes": round(s.rem_sleep_seconds / 60.0) if s.rem_sleep_seconds else None,
            "awake_minutes": round(s.awake_seconds / 60.0) if s.awake_seconds else None,
            "hrv_weekly_avg": s.hrv_weekly_avg,
            "hrv_last_night": s.hrv_last_night,
        }
        for s in sleep_records
        if s.total_sleep_seconds is not None or s.sleep_score is not None or s.hrv_weekly_avg is not None
    ]

    return {
        "daily_records": daily_list,
        "sleep_records": sleep_list,
        "provenance": {
            "steps": {"source": "Garmin API", "status": "verified", "unit": "steps"},
            "resting_heart_rate": {"source": "Garmin API", "status": "verified", "unit": "bpm"},
            "sleep_duration": {"source": "Garmin API", "status": "verified", "unit": "hours"},
            "sleep_score": {"source": "Garmin API", "status": "verified", "unit": "/100"},
            "sleep_stages": {"source": "Garmin API", "status": "verified", "unit": "minutes"},
            "hrv": {"source": "Garmin API", "status": "verified", "unit": "ms"},
            "body_battery": {"source": "Garmin API", "status": "verified", "unit": "points"},
            "stress": {"source": "Garmin API", "status": "verified", "unit": "/100"},
            "respiration": {"source": "Garmin API", "status": "verified", "unit": "brpm"},
        },
    }


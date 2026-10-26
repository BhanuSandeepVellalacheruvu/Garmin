"""Response normalizer: converts raw Garmin API dicts to provider DTOs."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.providers.garmin.base import (
    GarminActivity, GarminDailySummary, GarminHRVData, GarminSleepRecord,
)


def _safe_int(val: Any) -> int | None:
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _safe_float(val: Any) -> float | None:
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _parse_dt(val: Any) -> datetime | None:
    if not val:
        return None
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _parse_date(val: Any) -> date | None:
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(str(val)[:10])
    except Exception:
        return None


class GarminNormalizer:
    """Maps Garmin API response fields to provider DTOs.

    Field names are based on the Garmin Connect Personal API Swagger spec.
    Gracefully handles missing or renamed fields.
    """

    def normalize_activity(self, raw: dict) -> GarminActivity:
        # Try multiple known field name variants
        act_id = str(
            raw.get("activityId") or raw.get("activity_id") or raw.get("summaryId") or ""
        )
        sport = (
            raw.get("activityType", {}).get("typeKey")
            or raw.get("sport_type")
            or raw.get("activityTypeName")
            or "unknown"
        )
        start_raw = raw.get("startTimeLocal") or raw.get("startTimeGMT") or raw.get("start_time")
        return GarminActivity(
            garmin_activity_id=act_id,
            name=raw.get("activityName") or raw.get("name"),
            sport_type=sport.lower().replace(" ", "_"),
            activity_type=raw.get("activityType", {}).get("typeKey") if isinstance(raw.get("activityType"), dict) else raw.get("activity_type"),
            start_time=_parse_dt(start_raw) or datetime.now(timezone.utc),
            duration_seconds=_safe_float(raw.get("duration") or raw.get("elapsedDuration")),
            distance_meters=_safe_float(raw.get("distance")),
            avg_heart_rate=_safe_int(raw.get("averageHR") or raw.get("avgHr")),
            max_heart_rate=_safe_int(raw.get("maxHR") or raw.get("maxHr")),
            avg_speed_ms=_safe_float(raw.get("averageSpeed")),
            max_speed_ms=_safe_float(raw.get("maxSpeed")),
            elevation_gain=_safe_float(raw.get("elevationGain")),
            elevation_loss=_safe_float(raw.get("elevationLoss")),
            avg_cadence=_safe_int(raw.get("averageRunningCadenceInStepsPerMinute") or raw.get("averageBikingCadenceInRevPerMinute") or raw.get("avgCadence")),
            calories=_safe_int(raw.get("calories")),
            training_effect_aerobic=_safe_float(raw.get("aerobicTrainingEffect")),
            training_effect_anaerobic=_safe_float(raw.get("anaerobicTrainingEffect")),
            laps=raw.get("splitSummaries") or raw.get("laps") or [],
            raw_data=raw,
        )

    def normalize_daily_summary(self, raw: dict, cal_date: date) -> GarminDailySummary:
        return GarminDailySummary(
            calendar_date=cal_date,
            steps=_safe_int(raw.get("totalSteps") or raw.get("steps")),
            active_minutes=_safe_int(raw.get("activeKilocalories") and raw.get("moderateIntensityMinutes")),
            resting_heart_rate=_safe_int(raw.get("restingHeartRate")),
            avg_stress_level=_safe_int(raw.get("averageStressLevel")),
            body_battery_high=_safe_int(raw.get("bodyBatteryHighestValue")),
            body_battery_low=_safe_int(raw.get("bodyBatteryLowestValue")),
            respiration_avg=_safe_float(raw.get("avgWakingRespirationValue")),
        )

    def normalize_sleep(self, raw: dict) -> GarminSleepRecord:
        cal_date = _parse_date(raw.get("calendarDate") or raw.get("sleepStartTimestampLocal"))
        return GarminSleepRecord(
            calendar_date=cal_date or date.today(),
            sleep_start=_parse_dt(raw.get("sleepStartTimestampGMT")),
            sleep_end=_parse_dt(raw.get("sleepEndTimestampGMT")),
            total_sleep_seconds=_safe_int(raw.get("sleepTimeSeconds")),
            deep_sleep_seconds=_safe_int(raw.get("deepSleepSeconds")),
            light_sleep_seconds=_safe_int(raw.get("lightSleepSeconds")),
            rem_sleep_seconds=_safe_int(raw.get("remSleepSeconds")),
            awake_seconds=_safe_int(raw.get("awakeSleepSeconds")),
            sleep_score=_safe_int(raw.get("sleepScores", {}).get("overall", {}).get("value") if isinstance(raw.get("sleepScores"), dict) else raw.get("sleepScore")),
            hrv_weekly_avg=_safe_float(raw.get("avgOvernightHrv")),
            hrv_last_night=_safe_float(raw.get("hrvLastNight")),
            hrv_last_night_5min_high=_safe_float(raw.get("hfAverage")),
        )

    def normalize_hrv(self, raw: dict) -> GarminHRVData:
        return GarminHRVData(
            calendar_date=_parse_date(raw.get("calendarDate")) or date.today(),
            hrv_weekly_avg=_safe_float(raw.get("weeklyAvg")),
            hrv_last_night=_safe_float(raw.get("lastNight")),
            hrv_last_night_5min_high=_safe_float(raw.get("lastNight5MinHigh")),
        )

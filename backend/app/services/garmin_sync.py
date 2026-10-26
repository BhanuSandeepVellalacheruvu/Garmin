"""Garmin sync service — idempotent, recoverable data ingestion."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.activity import Activity, ActivityLap
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.sync import SyncJob
from app.models.user import UserProfile
from app.providers.garmin.base import GarminProvider, GarminActivity, GarminDailySummary, GarminSleepRecord
from app.models.base import new_uuid

log = logging.getLogger(__name__)

_MAX_HISTORY_DAYS = 365


class GarminSyncService:
    def __init__(self, db: AsyncSession, provider: GarminProvider, user_id: str) -> None:
        self.db = db
        self.provider = provider
        self.user_id = user_id

    # ── Job tracking ────────────────────────────────────────

    async def _start_job(self, job_type: str) -> SyncJob:
        job = SyncJob(
            id=new_uuid(),
            user_id=self.user_id,
            provider=self.provider.get_provider_name()[:30],
            job_type=job_type,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(job)
        await self.db.commit()
        return job

    async def _finish_job(self, job: SyncJob, records: int, error: str | None = None) -> None:
        if error:
            await self.db.rollback()
        job.status = "failed" if error else "success"
        job.completed_at = datetime.now(timezone.utc)
        job.records_synced = records
        job.error_message = error
        await self.db.commit()

    # ── Incremental sync ────────────────────────────────────

    async def run_incremental_sync(self) -> SyncJob:
        """Sync activities and health data since the last successful sync."""
        job = await self._start_job("incremental")
        try:
            # Determine date range
            last_job_result = await self.db.execute(
                select(SyncJob)
                .where(and_(SyncJob.user_id == self.user_id, SyncJob.status == "success"))
                .order_by(SyncJob.completed_at.desc())
                .limit(1)
            )
            last_job = last_job_result.scalar_one_or_none()
            if last_job and last_job.last_synced_date:
                start_date = date.fromisoformat(last_job.last_synced_date)
            else:
                start_date = date.today() - timedelta(days=90)
            end_date = date.today()

            records = await self._sync_range(start_date, end_date)
            job.last_synced_date = end_date.isoformat()
            await self._finish_job(job, records)
        except Exception as exc:
            log.exception("Incremental sync failed")
            await self._finish_job(job, 0, str(exc)[:500])
        return job

    async def run_full_sync(self, start_date: date, end_date: date) -> SyncJob:
        """Full historical import for a specified date range."""
        job = await self._start_job("full")
        try:
            records = await self._sync_range(start_date, end_date)
            job.last_synced_date = end_date.isoformat()
            await self._finish_job(job, records)
        except Exception as exc:
            log.exception("Full sync failed")
            await self._finish_job(job, 0, str(exc)[:500])
        return job

    # ── Core sync logic ─────────────────────────────────────

    async def _sync_range(self, start_date: date, end_date: date) -> int:
        total = 0
        log.info("Syncing %s → %s for user %s", start_date, end_date, self.user_id)

        # Authenticate once
        await self.provider.authenticate()

        # 1. Activities (paginated)
        try:
            offset = 0
            while True:
                activities = await self.provider.get_activities(
                    start_date, end_date, limit=100, offset=offset
                )
                if not activities:
                    break
                for act in activities:
                    upserted = await self._upsert_activity(act)
                    total += upserted
                if len(activities) < 100:
                    break
                offset += 100
            await self.db.commit()
            log.info("Activities synced: total running count %d", total)
        except Exception as exc:
            log.warning("Partial sync issue fetching activities: %s", exc)
            await self.db.rollback()

        # 2. Daily health metrics (deduplicated by calendar_date)
        try:
            summaries = await self.provider.get_daily_summaries(start_date, end_date)
            unique_summaries = list({s.calendar_date: s for s in summaries}.values())
            for s in unique_summaries:
                await self._upsert_daily_health(s)
                total += 1
            await self.db.commit()
            log.info("Daily summaries synced: total running count %d", total)
        except Exception as exc:
            log.warning("Partial sync issue fetching daily summaries: %s", exc)
            await self.db.rollback()

        # 3. Sleep records (deduplicated by calendar_date)
        try:
            sleep_records = await self.provider.get_sleep(start_date, end_date)
            unique_sleep = list({sr.calendar_date: sr for sr in sleep_records}.values())
            for sr in unique_sleep:
                await self._upsert_sleep(sr)
                total += 1
            await self.db.commit()
            log.info("Sleep records synced: total running count %d", total)
        except Exception as exc:
            log.warning("Partial sync issue fetching sleep records: %s", exc)
            await self.db.rollback()

        # 4. HRV trends
        try:
            hrv_records = await self.provider.get_hrv(start_date, end_date)
            unique_hrv = list({h.calendar_date: h for h in hrv_records}.values())
            for h in unique_hrv:
                result = await self.db.execute(
                    select(SleepRecord).where(
                        and_(SleepRecord.user_id == self.user_id, SleepRecord.calendar_date == h.calendar_date)
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    existing.hrv_weekly_avg = h.hrv_weekly_avg
                    existing.hrv_last_night = h.hrv_last_night
                    existing.hrv_last_night_5min_high = h.hrv_last_night_5min_high
                else:
                    self.db.add(SleepRecord(
                        id=new_uuid(),
                        user_id=self.user_id,
                        calendar_date=h.calendar_date,
                        hrv_weekly_avg=h.hrv_weekly_avg,
                        hrv_last_night=h.hrv_last_night,
                        hrv_last_night_5min_high=h.hrv_last_night_5min_high,
                        is_demo=False,
                    ))
            await self.db.commit()
            log.info("HRV trends synced successfully")
        except Exception as exc:
            log.warning("Partial sync issue fetching HRV: %s", exc)
            await self.db.rollback()

        log.info("Sync complete: %d records processed", total)
        return total

    # ── Upsert helpers (idempotent) ─────────────────────────

    async def _upsert_activity(self, act: GarminActivity) -> int:
        """Insert or update activity by garmin_activity_id. Returns 1 if written."""
        result = await self.db.execute(
            select(Activity).where(Activity.garmin_activity_id == act.garmin_activity_id)
        )
        existing = result.scalar_one_or_none()
        is_demo = self.provider.get_provider_name().startswith("Mock")

        if existing:
            # Update fields that may have changed
            existing.name = act.name
            existing.duration_seconds = act.duration_seconds
            existing.distance_meters = act.distance_meters
            existing.avg_heart_rate = act.avg_heart_rate
            existing.max_heart_rate = act.max_heart_rate
            existing.avg_speed_ms = act.avg_speed_ms
            existing.elevation_gain = act.elevation_gain
            existing.avg_cadence = act.avg_cadence
            existing.calories = act.calories
            return 0  # Not a new record
        else:
            new_act = Activity(
                id=new_uuid(),
                garmin_activity_id=act.garmin_activity_id,
                user_id=self.user_id,
                name=act.name,
                sport_type=act.sport_type,
                activity_type=act.activity_type,
                start_time=act.start_time,
                duration_seconds=act.duration_seconds,
                distance_meters=act.distance_meters,
                avg_heart_rate=act.avg_heart_rate,
                max_heart_rate=act.max_heart_rate,
                avg_speed_ms=act.avg_speed_ms,
                max_speed_ms=act.max_speed_ms,
                elevation_gain=act.elevation_gain,
                elevation_loss=act.elevation_loss,
                avg_cadence=act.avg_cadence,
                calories=act.calories,
                training_effect_aerobic=act.training_effect_aerobic,
                training_effect_anaerobic=act.training_effect_anaerobic,
                raw_data={},  # Don't store full raw_data to save space
                is_demo=is_demo,
            )
            self.db.add(new_act)
            await self.db.flush()

            # Store laps
            for i, lap in enumerate(act.laps or []):
                self.db.add(ActivityLap(
                    id=new_uuid(),
                    activity_id=new_act.id,
                    lap_index=i,
                    start_time=None,
                    duration_seconds=lap.get("duration") or lap.get("totalElapsedTime"),
                    distance_meters=lap.get("distance"),
                    avg_heart_rate=lap.get("averageHR"),
                    avg_speed_ms=lap.get("averageSpeed"),
                    avg_cadence=lap.get("averageCadence"),
                    elevation_gain=lap.get("elevationGain"),
                ))
            return 1

    async def _upsert_daily_health(self, s: GarminDailySummary) -> None:
        result = await self.db.execute(
            select(DailyHealthMetric).where(
                and_(DailyHealthMetric.user_id == self.user_id, DailyHealthMetric.calendar_date == s.calendar_date)
            )
        )
        existing = result.scalar_one_or_none()
        is_demo = self.provider.get_provider_name().startswith("Mock")
        if existing:
            existing.steps = s.steps
            existing.resting_heart_rate = s.resting_heart_rate
            existing.avg_stress_level = s.avg_stress_level
            existing.body_battery_high = s.body_battery_high
            existing.body_battery_low = s.body_battery_low
            existing.respiration_avg = s.respiration_avg
        else:
            self.db.add(DailyHealthMetric(
                id=new_uuid(),
                user_id=self.user_id,
                calendar_date=s.calendar_date,
                steps=s.steps,
                active_minutes=s.active_minutes,
                resting_heart_rate=s.resting_heart_rate,
                avg_stress_level=s.avg_stress_level,
                body_battery_high=s.body_battery_high,
                body_battery_low=s.body_battery_low,
                respiration_avg=s.respiration_avg,
                is_demo=is_demo,
            ))

    async def _upsert_sleep(self, sr: GarminSleepRecord) -> None:
        result = await self.db.execute(
            select(SleepRecord).where(
                and_(SleepRecord.user_id == self.user_id, SleepRecord.calendar_date == sr.calendar_date)
            )
        )
        existing = result.scalar_one_or_none()
        is_demo = self.provider.get_provider_name().startswith("Mock")
        if existing:
            existing.total_sleep_seconds = sr.total_sleep_seconds
            existing.deep_sleep_seconds = sr.deep_sleep_seconds
            existing.light_sleep_seconds = sr.light_sleep_seconds
            existing.rem_sleep_seconds = sr.rem_sleep_seconds
            existing.sleep_score = sr.sleep_score
            existing.hrv_last_night = sr.hrv_last_night
            existing.hrv_weekly_avg = sr.hrv_weekly_avg
        else:
            self.db.add(SleepRecord(
                id=new_uuid(),
                user_id=self.user_id,
                calendar_date=sr.calendar_date,
                sleep_start=sr.sleep_start,
                sleep_end=sr.sleep_end,
                total_sleep_seconds=sr.total_sleep_seconds,
                deep_sleep_seconds=sr.deep_sleep_seconds,
                light_sleep_seconds=sr.light_sleep_seconds,
                rem_sleep_seconds=sr.rem_sleep_seconds,
                awake_seconds=sr.awake_seconds,
                sleep_score=sr.sleep_score,
                hrv_weekly_avg=sr.hrv_weekly_avg,
                hrv_last_night=sr.hrv_last_night,
                hrv_last_night_5min_high=sr.hrv_last_night_5min_high,
                is_demo=is_demo,
            ))

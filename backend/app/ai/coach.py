"""AI coach rules-based recommendation layer."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from app.analytics.running import ActivityRow, calculate_acute_load, calculate_chronic_load, acwr
from app.analytics.health import HealthRow, SleepRow


@dataclass
class Recommendation:
    category: Literal["workout", "recovery", "volume", "caution"]
    title: str
    rationale: str
    action: str
    confidence: Literal["high", "moderate", "low"]
    caveat: str


class TrainingCoach:
    """Rules-based engine analyzing load, recovery, and consistency."""

    def analyze(
        self,
        activities: list[ActivityRow],
        health_metrics: list[HealthRow],
        sleep_records: list[SleepRow],
        race_goal: dict | None = None,
    ) -> list[Recommendation]:
        recs: list[Recommendation] = []

        if not activities:
            recs.append(
                Recommendation(
                    category="volume",
                    title="Begin Base Building",
                    rationale="No recent training sessions recorded in the database.",
                    action="Schedule 2 to 3 easy sessions of 20–30 minutes this week at a conversational effort.",
                    confidence="high",
                    caveat="Listen to your body and avoid ramping up volume too quickly.",
                )
            )
            return recs

        # 1. ACWR Analysis
        acute = calculate_acute_load(activities, days=7)
        chronic = calculate_chronic_load(activities, days=28)
        ratio = acwr(acute, chronic)

        if ratio is not None:
            if ratio > 1.4:
                recs.append(
                    Recommendation(
                        category="caution",
                        title="Elevated Acute Workload Spike",
                        rationale=f"Your estimated acute:chronic workload ratio is {ratio:.2f} (> 1.40). Recent training volume has accelerated faster than chronic fitness base.",
                        action="Prioritize active recovery, keep any planned runs strictly in Zone 1/2, or take an extra rest day.",
                        confidence="high",
                        caveat="ACWR is an application-derived estimate based on duration/heart rate, not a medical or diagnostic measurement.",
                    )
                )
            elif ratio < 0.75 and len(activities) >= 4:
                recs.append(
                    Recommendation(
                        category="volume",
                        title="Training Stimulus Underload",
                        rationale=f"Estimated ACWR is {ratio:.2f} (< 0.75). Training load has significantly decreased compared to your monthly baseline.",
                        action="Gradually introduce a quality workout or modestly increase weekly mileage by 5-10%.",
                        confidence="moderate",
                        caveat="If you are tapering for an upcoming race or recovering from illness, a low ACWR is expected and intentional.",
                    )
                )

        # 2. Sleep & HRV Recovery Signal
        recent_sleep = sorted(sleep_records, key=lambda s: s.calendar_date)[-3:]
        if recent_sleep:
            poor_sleep_days = sum(1 for s in recent_sleep if (s.sleep_score and s.sleep_score < 65) or (s.total_sleep_seconds and s.total_sleep_seconds < 6 * 3600))
            if poor_sleep_days >= 2:
                recs.append(
                    Recommendation(
                        category="recovery",
                        title="Cumulative Sleep Debt Detected",
                        rationale=f"In {poor_sleep_days} of your last 3 nights, sleep duration was under 6 hours or sleep score dropped below 65.",
                        action="Shift intense interval workouts to later in the week and focus on an extra 45–60 minutes of sleep hygiene tonight.",
                        confidence="moderate",
                        caveat="Optical sleep staging can have measurement variance; prioritize subjective feelings of fatigue.",
                    )
                )

        # 3. Race Goal Specifics
        if race_goal and race_goal.get("target_date"):
            recs.append(
                Recommendation(
                    category="workout",
                    title=f"Preparation for {race_goal.get('name', 'Goal Race')}",
                    rationale=f"Target race distance: {race_goal.get('distance_meters', 0)/1000:.1f} km scheduled on {race_goal.get('target_date')}.",
                    action="Ensure at least one weekly continuous long run representing 25–30% of total weekly mileage.",
                    confidence="moderate",
                    caveat="Pacing strategies must be tested during training sessions before race day.",
                )
            )

        # Default recommendation if none triggered
        if not recs:
            recs.append(
                Recommendation(
                    category="workout",
                    title="Maintain Balanced Progression",
                    rationale="Your training frequency, acute:chronic workload balance, and recovery markers remain in equilibrium.",
                    action="Proceed with your planned workouts, keeping 80% of volume at an easy aerobic effort and 20% at quality threshold/intervals.",
                    confidence="high",
                    caveat="Ensure adequate hydration and post-run nutrition.",
                )
            )

        return recs

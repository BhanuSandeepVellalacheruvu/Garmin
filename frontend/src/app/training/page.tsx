"use client";

import React from "react";
import useSWR from "swr";
import {
  Target,
  Flame,
  Zap,
  Activity,
  Heart,
  TrendingUp,
  BarChart3,
  Clock,
  Gauge,
  Calendar,
  ShieldCheck,
  Footprints,
  Compass,
  Moon,
} from "lucide-react";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";
import { fetchAPI } from "@/lib/api";

interface TrainingLoadResponse {
  acute_load_7d: number;
  chronic_load_28d: number;
  acwr: number | null;
  status: string;
  note: string;
}

interface RunningFullSuiteResponse {
  activities_count: number;
  activities: {
    id: string;
    garmin_id: string;
    name: string;
    date: string;
    distance_km: number;
    duration_seconds: number;
    duration_formatted: string;
    avg_pace_sec: number;
    avg_pace_formatted: string;
    avg_heart_rate: number | null;
    avg_cadence: number | null;
    stride_length_m: number | null;
    elevation_gain_m: number | null;
    calories: number | null;
    training_effect_aerobic: number | null;
    training_effect_anaerobic: number | null;
  }[];
  weekly_volume: {
    week_start: string;
    distance_km: number;
    duration_hours: number;
    runs_count: number;
  }[];
}

interface HealthFullSuiteResponse {
  daily_records: {
    date: string;
    resting_heart_rate: number | null;
  }[];
  sleep_records: {
    date: string;
    sleep_score: number | null;
    total_sleep_hours: number | null;
  }[];
}

export default function TrainingLoadPage() {
  const { data: loadData } = useSWR<TrainingLoadResponse>("/analytics/training-load", fetchAPI);
  const { data: runningData } = useSWR<RunningFullSuiteResponse>("/analytics/running/full-suite", fetchAPI);
  const { data: healthData } = useSWR<HealthFullSuiteResponse>("/analytics/health/full-suite?days=30", fetchAPI);

  const activities = runningData?.activities || [];
  const weekly = runningData?.weekly_volume || [];
  const dailyHealth = healthData?.daily_records || [];
  const sleepRecords = healthData?.sleep_records || [];

  const acuteVal = loadData?.acute_load_7d ? Math.round(loadData.acute_load_7d) : null;
  const chronicVal = loadData?.chronic_load_28d ? Math.round(loadData.chronic_load_28d) : null;
  const acwrVal = loadData?.acwr ?? null;
  const tsbVal = chronicVal !== null && acuteVal !== null ? chronicVal - acuteVal : null;

  // Real Data Bindings (Zero modulo loops)
  const acuteData: DataPoint[] = acuteVal !== null ? [{ date: "Current 7d", value: acuteVal }] : [];
  const chronicData: DataPoint[] = chronicVal !== null ? [{ date: "Current 28d", value: chronicVal }] : [];
  const acwrData: DataPoint[] = acwrVal !== null ? [{ date: "Current ACWR", value: acwrVal }] : [];
  const tsbData: DataPoint[] = tsbVal !== null ? [{ date: "Current TSB", value: tsbVal }] : [];

  const weeklyMileageData: DataPoint[] = weekly.map((w) => ({
    date: w.week_start,
    value: w.distance_km,
  }));

  const weeklyDurationData: DataPoint[] = weekly.map((w) => ({
    date: w.week_start,
    value: w.duration_hours,
  }));

  const aerobicEffectData: DataPoint[] = activities
    .filter((a) => a.training_effect_aerobic !== null)
    .map((a) => ({ date: a.date, value: a.training_effect_aerobic, name: a.name }));

  const anaerobicEffectData: DataPoint[] = activities
    .filter((a) => a.training_effect_anaerobic !== null)
    .map((a) => ({ date: a.date, value: a.training_effect_anaerobic, name: a.name }));

  const cadenceData: DataPoint[] = activities
    .filter((a) => a.avg_cadence !== null)
    .map((a) => ({ date: a.date, value: a.avg_cadence, name: a.name }));

  const strideData: DataPoint[] = activities
    .filter((a) => a.stride_length_m !== null)
    .map((a) => ({ date: a.date, value: a.stride_length_m, name: a.name }));

  const elevationData: DataPoint[] = activities
    .filter((a) => a.elevation_gain_m !== null)
    .map((a) => ({ date: a.date, value: a.elevation_gain_m, name: a.name }));

  const caloriesData: DataPoint[] = activities
    .filter((a) => a.calories !== null)
    .map((a) => ({ date: a.date, value: a.calories, name: a.name }));

  const rhrTrendData: DataPoint[] = dailyHealth
    .filter((d) => d.resting_heart_rate !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.resting_heart_rate }));

  const sleepScoreData: DataPoint[] = sleepRecords
    .filter((s) => s.sleep_score !== null)
    .slice(-14)
    .map((s) => ({ date: s.date, value: s.sleep_score }));

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5" /> Workload & Recovery Science
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Training Load & Adaptation
          </h1>
          <p className="text-xs md:text-sm text-gray-400 mt-1">
            Deterministic workload models and authentic cardiovascular adaptation indicators.
            No synthetic waveforms.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] px-3 py-1 rounded-full border font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            Deterministic Python Model
          </span>
        </div>
      </div>

      {/* Grid of 14 Individual Dedicated Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Chart 1: Acute Load */}
        <MetricDetailChart
          title="Acute Workload (7-Day)"
          description="Fatigue accumulation over the past 7 days"
          currentValue={acuteVal !== null ? acuteVal : "—"}
          unit="load"
          data={acuteData}
          type="bar"
          color="cyan"
          icon={Flame}
          provenance={{ source: "Calculated (App)", status: "calculated", unit: "load" }}
        />

        {/* Chart 2: Chronic Load */}
        <MetricDetailChart
          title="Chronic Workload (28-Day)"
          description="Long-term aerobic fitness baseline accumulated over 4 weeks"
          currentValue={chronicVal !== null ? chronicVal : "—"}
          unit="load"
          data={chronicData}
          type="bar"
          color="blue"
          icon={Activity}
          provenance={{ source: "Calculated (App)", status: "calculated", unit: "load" }}
        />

        {/* Chart 3: ACWR */}
        <MetricDetailChart
          title="Acute:Chronic Workload Ratio (ACWR)"
          description="Gabbett workload index (sweet spot 0.8 - 1.3 for injury prevention)"
          currentValue={acwrVal !== null ? acwrVal : "—"}
          unit="ratio"
          data={acwrData}
          type="bar"
          color="emerald"
          icon={Gauge}
          badge={acwrVal && acwrVal > 1.3 ? "Elevated Load" : "Optimal Range"}
          badgeVariant={acwrVal && acwrVal > 1.3 ? "warning" : "success"}
          provenance={{ source: "Calculated (App)", status: "calculated", unit: "ratio" }}
        />

        {/* Chart 4: Training Stress Balance */}
        <MetricDetailChart
          title="Training Stress Balance (TSB)"
          description="Freshness vs fatigue margin (Chronic minus Acute load)"
          currentValue={tsbVal !== null ? tsbVal : "—"}
          unit="pts"
          data={tsbData}
          type="bar"
          color="violet"
          icon={TrendingUp}
          provenance={{ source: "Calculated (App)", status: "calculated", unit: "pts" }}
        />

        {/* Chart 5: Weekly Mileage */}
        <MetricDetailChart
          title="Weekly Running Mileage"
          description="Total kilometers completed per calendar week"
          currentValue={weekly.length > 0 ? weekly[weekly.length - 1].distance_km : 0}
          unit="km"
          data={weeklyMileageData}
          type="bar"
          color="cyan"
          icon={BarChart3}
          provenance={{ source: "Garmin API", status: "verified", unit: "km" }}
        />

        {/* Chart 6: Weekly Duration */}
        <MetricDetailChart
          title="Weekly Time on Feet"
          description="Total aerobic running hours per week"
          currentValue={weekly.length > 0 ? `${weekly[weekly.length - 1].duration_hours}h` : "0h"}
          unit="hours"
          data={weeklyDurationData}
          type="bar"
          color="blue"
          icon={Clock}
          provenance={{ source: "Garmin API", status: "verified", unit: "hours" }}
        />

        {/* Chart 7: Aerobic Training Effect */}
        <MetricDetailChart
          title="Aerobic Stimulus (TE)"
          description="Garmin Aerobic Training Effect per session"
          currentValue={activities.length > 0 ? activities[activities.length - 1].training_effect_aerobic : "—"}
          unit="/ 5.0"
          data={aerobicEffectData}
          type="area"
          color="emerald"
          icon={Zap}
          provenance={{ source: "Garmin API", status: "verified", unit: "score" }}
        />

        {/* Chart 8: Anaerobic Training Effect */}
        <MetricDetailChart
          title="Anaerobic Stimulus (TE)"
          description="Garmin Anaerobic Training Effect per session"
          currentValue={activities.length > 0 ? activities[activities.length - 1].training_effect_anaerobic : "0.0"}
          unit="/ 5.0"
          data={anaerobicEffectData}
          type="area"
          color="orange"
          icon={Zap}
          provenance={{ source: "Garmin API", status: "verified", unit: "score" }}
        />

        {/* Chart 9: Session Cadence */}
        <MetricDetailChart
          title="Session Running Cadence"
          description="Average steps per minute across completed workouts"
          currentValue={activities.length > 0 ? activities[activities.length - 1].avg_cadence : "—"}
          unit="spm"
          data={cadenceData}
          type="line"
          color="violet"
          icon={Footprints}
          provenance={{ source: "Garmin API", status: "verified", unit: "spm" }}
        />

        {/* Chart 10: Stride Length */}
        <MetricDetailChart
          title="Stride Length Adaptation"
          description="Calculated stride length (speed * 60) / cadence"
          currentValue={activities.length > 0 ? activities[activities.length - 1].stride_length_m : "—"}
          unit="m"
          data={strideData}
          type="line"
          color="cyan"
          icon={Compass}
          provenance={{ source: "Calculated (Speed/Cadence)", status: "calculated", unit: "m" }}
        />

        {/* Chart 11: Elevation Climed */}
        <MetricDetailChart
          title="Elevation Climb"
          description="Vertical meters ascended per workout"
          currentValue={activities.length > 0 ? activities[activities.length - 1].elevation_gain_m : "0"}
          unit="m"
          data={elevationData}
          type="bar"
          color="amber"
          icon={TrendingUp}
          provenance={{ source: "Garmin API", status: "verified", unit: "m" }}
        />

        {/* Chart 12: Calories Burned */}
        <MetricDetailChart
          title="Caloric Expenditure"
          description="Energy burned during workouts"
          currentValue={activities.length > 0 ? activities[activities.length - 1].calories : "—"}
          unit="kcal"
          data={caloriesData}
          type="bar"
          color="rose"
          icon={Flame}
          provenance={{ source: "Garmin API", status: "verified", unit: "kcal" }}
        />

        {/* Chart 13: Resting Heart Rate Trend */}
        <MetricDetailChart
          title="Basal Resting Heart Rate"
          description="Overnight cardiovascular recovery baseline"
          currentValue={dailyHealth.length > 0 ? dailyHealth[dailyHealth.length - 1].resting_heart_rate : "—"}
          unit="bpm"
          data={rhrTrendData}
          type="line"
          color="rose"
          icon={Heart}
          provenance={{ source: "Garmin API", status: "verified", unit: "bpm" }}
        />

        {/* Chart 14: Sleep Recovery Score */}
        <MetricDetailChart
          title="Nightly Sleep Recovery Score"
          description="Garmin sleep score reflecting physiological rejuvenation"
          currentValue={sleepRecords.length > 0 ? sleepRecords[sleepRecords.length - 1].sleep_score : "—"}
          unit="/ 100"
          data={sleepScoreData}
          type="line"
          color="violet"
          icon={Moon}
          provenance={{ source: "Garmin API", status: "verified", unit: "/100" }}
        />
      </div>
    </div>
  );
}

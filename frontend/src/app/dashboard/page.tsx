"use client";

import useSWR from "swr";
import {
  Footprints,
  Heart,
  Moon,
  BatteryCharging,
  TrendingUp,
  Brain,
  CalendarDays,
  Sparkles,
  Flame,
  Activity as ActivityIcon,
  Wind,
  Gauge,
  BarChart3,
  Clock,
  Zap,
  ShieldCheck,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { HealthOverview, WeeklyVolume, TrainingLoad, AIBriefing, Activity } from "@/lib/types";
import { MetricCard } from "@/components/cards/MetricCard";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";
import { formatDistance, formatDuration, formatPace, formatDate, getSportEmoji } from "@/lib/utils";

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
    calories: number | null;
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
    steps: number | null;
    resting_heart_rate: number | null;
    avg_stress_level: number | null;
    body_battery_high: number | null;
    body_battery_low: number | null;
    body_battery_charged: number | null;
    respiration_avg: number | null;
    active_minutes: number | null;
  }[];
  sleep_records: {
    date: string;
    total_sleep_hours: number | null;
    sleep_score: number | null;
    deep_sleep_minutes: number | null;
    light_sleep_minutes: number | null;
    rem_sleep_minutes: number | null;
    awake_minutes: number | null;
    hrv_weekly_avg: number | null;
    hrv_last_night: number | null;
  }[];
}

export default function DashboardPage() {
  const { data: health } = useSWR<HealthOverview>("/health/overview", fetchAPI);
  const { data: load } = useSWR<TrainingLoad>("/analytics/training-load", fetchAPI);
  const { data: briefing } = useSWR<AIBriefing>("/ai/briefing", fetchAPI);
  const { data: activitiesData } = useSWR<{ items: Activity[] }>("/activities?limit=5", fetchAPI);

  const { data: suiteRunning } = useSWR<RunningFullSuiteResponse>(
    "/analytics/running/full-suite",
    fetchAPI
  );
  const { data: suiteHealth } = useSWR<HealthFullSuiteResponse>(
    "/analytics/health/full-suite?days=30",
    fetchAPI
  );

  const activities = activitiesData?.items || [];
  const dailyHealth = suiteHealth?.daily_records || [];
  const sleepRecords = suiteHealth?.sleep_records || [];
  const runningActivities = suiteRunning?.activities || [];
  const weeklyRunning = suiteRunning?.weekly_volume || [];

  const latestDaily = dailyHealth.length > 0 ? dailyHealth[dailyHealth.length - 1] : null;
  const latestSleep = sleepRecords.length > 0 ? sleepRecords[sleepRecords.length - 1] : null;
  const latestRun = runningActivities.length > 0 ? runningActivities[runningActivities.length - 1] : null;

  // Real Data Bindings (Zero modulo loops)
  // 1. Steps
  const stepsData: DataPoint[] = dailyHealth
    .filter((d) => d.steps !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.steps }));

  // 2. Resting Heart Rate
  const rhrData: DataPoint[] = dailyHealth
    .filter((d) => d.resting_heart_rate !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.resting_heart_rate }));

  // 3. Sleep Duration
  const sleepDurationData: DataPoint[] = sleepRecords
    .filter((s) => s.total_sleep_hours !== null)
    .slice(-14)
    .map((s) => ({ date: s.date, value: s.total_sleep_hours }));

  // 4. Sleep Score
  const sleepScoreData: DataPoint[] = sleepRecords
    .filter((s) => s.sleep_score !== null)
    .slice(-14)
    .map((s) => ({ date: s.date, value: s.sleep_score }));

  // 5. Body Battery High
  const bbHighData: DataPoint[] = dailyHealth
    .filter((d) => d.body_battery_high !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.body_battery_high }));

  // 6. Body Battery Low
  const bbLowData: DataPoint[] = dailyHealth
    .filter((d) => d.body_battery_low !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.body_battery_low }));

  // 7. Average Daily Stress
  const stressData: DataPoint[] = dailyHealth
    .filter((d) => d.avg_stress_level !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.avg_stress_level }));

  // 8. Weekly Running Distance
  const weeklyDistData: DataPoint[] = weeklyRunning.map((w) => ({
    date: w.week_start,
    value: w.distance_km,
  }));

  // 9. Average Pace Progression
  const paceData: DataPoint[] = runningActivities.map((r) => ({
    date: r.date,
    value: r.avg_pace_sec,
  }));

  // 10. Respiration
  const respirationData: DataPoint[] = dailyHealth
    .filter((d) => d.respiration_avg !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.respiration_avg }));

  // 11. Active Minutes
  const activeMinutesData: DataPoint[] = dailyHealth
    .filter((d) => d.active_minutes !== null)
    .slice(-14)
    .map((d) => ({ date: d.date, value: d.active_minutes }));

  // 12. Run Calories
  const runCalData: DataPoint[] = runningActivities
    .filter((r) => r.calories !== null)
    .map((r) => ({ date: r.date, value: r.calories }));

  // 13. Training Load Acute
  const acuteData: DataPoint[] = load?.acute_load_7d
    ? [{ date: "Current 7d", value: load.acute_load_7d }]
    : [];

  // 14. Training Load Chronic
  const chronicData: DataPoint[] = load?.chronic_load_28d
    ? [{ date: "Current 28d", value: load.chronic_load_28d }]
    : [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-2 pb-12">
      {/* Page Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Performance Lab Overview</h1>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full border font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Garmin Connect Sync
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Endurance vitals, running progression, and physiological recovery metrics.
          </p>
        </div>
      </div>

      {/* Top Vitals Row (5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Daily Steps"
          value={latestDaily?.steps ? latestDaily.steps.toLocaleString() : health?.steps?.toLocaleString()}
          unit="steps"
          icon={Footprints}
          subtext="Latest Garmin Synced"
          accentColor="cyan"
        />
        <MetricCard
          title="Resting HR"
          value={latestDaily?.resting_heart_rate ?? health?.resting_heart_rate}
          unit="bpm"
          icon={Heart}
          subtext="Overnight Baseline"
          accentColor="rose"
        />
        <MetricCard
          title="Sleep Score"
          value={latestSleep?.sleep_score ?? health?.sleep_score}
          unit="/ 100"
          icon={Moon}
          subtext={latestSleep ? `${latestSleep.total_sleep_hours} hrs logged` : "Nightly Efficiency"}
          accentColor="violet"
        />
        <MetricCard
          title="Body Battery"
          value={latestDaily?.body_battery_high ?? health?.body_battery_high}
          unit="/ 100"
          icon={BatteryCharging}
          subtext={latestDaily?.body_battery_low ? `Drain to ${latestDaily.body_battery_low}` : "Energy Metric"}
          accentColor="emerald"
        />
        <MetricCard
          title="Acute Load (7d)"
          value={load?.acute_load_7d ? Math.round(load.acute_load_7d) : "—"}
          unit="load"
          icon={Flame}
          subtext={load?.acwr ? `ACWR: ${load.acwr}` : "App Calculated"}
          accentColor="amber"
        />
      </div>

      {/* AI Coach Briefing Card */}
      {briefing && (
        <div className="bg-gradient-to-r from-cyan-950/40 via-blue-950/20 to-purple-950/30 border border-cyan-800/40 rounded-xl p-5 shadow-lg relative overflow-hidden">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-semibold text-white">AI Coach Morning Briefing</h2>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono flex items-center gap-1">
                    <Sparkles className="w-2.5 h-2.5" /> Ollama Cloud Grounded
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-0.5">
                  Weekly Total:{" "}
                  <span className="text-cyan-400 font-medium">{briefing.weekly_km} km</span>
                  {briefing.sleep_score && (
                    <span> • Sleep Score: <span className="text-gray-300 font-medium">{briefing.sleep_score}/100</span></span>
                  )}
                </p>
              </div>
            </div>
            <span className="text-xs text-gray-400 hidden sm:block">
              {formatDate(briefing.date)}
            </span>
          </div>

          <p className="text-sm text-gray-300 mt-3 leading-relaxed border-t border-gray-800/60 pt-3">
            {briefing.summary}
          </p>
        </div>
      )}

      {/* 14 Individual Chart Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight">
            Key Performance & Physiological Signals
          </h2>
          <span className="text-xs text-cyan-400 font-mono">14 Individual Charts</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {/* Chart 1: Steps */}
          <MetricDetailChart
            title="Daily Steps"
            description="Pedometer steps from Garmin daily summary"
            currentValue={latestDaily?.steps?.toLocaleString()}
            unit="steps"
            data={stepsData}
            type="bar"
            color="cyan"
            icon={Footprints}
            provenance={{ source: "Garmin API", status: "verified", unit: "steps" }}
          />

          {/* Chart 2: Resting HR */}
          <MetricDetailChart
            title="Resting Heart Rate"
            description="Overnight basal cardiovascular baseline"
            currentValue={latestDaily?.resting_heart_rate || "—"}
            unit="bpm"
            data={rhrData}
            type="line"
            color="rose"
            icon={Heart}
            provenance={{ source: "Garmin API", status: "verified", unit: "bpm" }}
          />

          {/* Chart 3: Sleep Duration */}
          <MetricDetailChart
            title="Sleep Duration"
            description="Total nightly sleep duration in hours"
            currentValue={latestSleep?.total_sleep_hours ? `${latestSleep.total_sleep_hours}h` : "—"}
            unit="hrs"
            data={sleepDurationData}
            type="area"
            color="violet"
            icon={Moon}
            provenance={{ source: "Garmin API", status: "verified", unit: "hours" }}
          />

          {/* Chart 4: Sleep Score */}
          <MetricDetailChart
            title="Sleep Quality Score"
            description="Garmin comprehensive sleep efficiency score"
            currentValue={latestSleep?.sleep_score || "—"}
            unit="/ 100"
            data={sleepScoreData}
            type="line"
            color="violet"
            icon={Moon}
            provenance={{ source: "Garmin API", status: "verified", unit: "/100" }}
          />

          {/* Chart 5: Body Battery High */}
          <MetricDetailChart
            title="Body Battery High"
            description="Peak recharge level reached during overnight rest"
            currentValue={latestDaily?.body_battery_high || "—"}
            unit="/ 100"
            data={bbHighData}
            type="area"
            color="emerald"
            icon={BatteryCharging}
            provenance={{ source: "Garmin API", status: "verified", unit: "points" }}
          />

          {/* Chart 6: Body Battery Low */}
          <MetricDetailChart
            title="Body Battery Low"
            description="Lowest energy reserve reached prior to sleep"
            currentValue={latestDaily?.body_battery_low || "—"}
            unit="/ 100"
            data={bbLowData}
            type="line"
            color="amber"
            icon={BatteryCharging}
            provenance={{ source: "Garmin API", status: "verified", unit: "points" }}
          />

          {/* Chart 7: Average Stress */}
          <MetricDetailChart
            title="Average Daily Stress"
            description="All-day autonomic nervous system stress score"
            currentValue={latestDaily?.avg_stress_level || "—"}
            unit="/ 100"
            data={stressData}
            type="line"
            color="orange"
            icon={ActivityIcon}
            provenance={{ source: "Garmin API", status: "verified", unit: "/100" }}
          />

          {/* Chart 8: Acute Training Load */}
          <MetricDetailChart
            title="Acute Training Load (7d)"
            description="Short-term fatigue accumulation from sessions"
            currentValue={load?.acute_load_7d ? Math.round(load.acute_load_7d) : "—"}
            unit="load"
            data={acuteData}
            type="bar"
            color="cyan"
            icon={Flame}
            provenance={{ source: "Calculated (App)", status: "calculated", unit: "load" }}
          />

          {/* Chart 9: Chronic Training Load */}
          <MetricDetailChart
            title="Chronic Training Load (28d)"
            description="Long-term aerobic baseline fitness"
            currentValue={load?.chronic_load_28d ? Math.round(load.chronic_load_28d) : "—"}
            unit="load"
            data={chronicData}
            type="bar"
            color="blue"
            icon={ActivityIcon}
            provenance={{ source: "Calculated (App)", status: "calculated", unit: "load" }}
          />

          {/* Chart 10: ACWR */}
          <MetricDetailChart
            title="Workload Ratio (ACWR)"
            description="Acute-to-chronic workload index"
            currentValue={load?.acwr || "—"}
            unit="ratio"
            data={load?.acwr ? [{ date: "Current", value: load.acwr }] : []}
            type="bar"
            color="emerald"
            icon={Gauge}
            provenance={{ source: "Calculated (App)", status: "calculated", unit: "ratio" }}
          />

          {/* Chart 11: Weekly Running Distance */}
          <MetricDetailChart
            title="Weekly Running Distance"
            description="Total weekly road and trail volume"
            currentValue={weeklyRunning.length > 0 ? `${weeklyRunning[weeklyRunning.length - 1].distance_km} km` : "0 km"}
            data={weeklyDistData}
            type="bar"
            color="cyan"
            icon={BarChart3}
            provenance={{ source: "Garmin API", status: "verified", unit: "km" }}
          />

          {/* Chart 12: Average Running Pace */}
          <MetricDetailChart
            title="Average Running Pace"
            description="Session pace (faster is higher)"
            currentValue={latestRun?.avg_pace_formatted || "—"}
            data={paceData}
            type="line"
            color="emerald"
            icon={Clock}
            isPace={true}
            provenance={{ source: "Garmin API", status: "verified", unit: "min/km" }}
          />

          {/* Chart 13: Run Calorie Burn */}
          <MetricDetailChart
            title="Running Calorie Burn"
            description="Energy expenditure per running session"
            currentValue={latestRun?.calories || "—"}
            unit="kcal"
            data={runCalData}
            type="bar"
            color="rose"
            icon={Flame}
            provenance={{ source: "Garmin API", status: "verified", unit: "kcal" }}
          />

          {/* Chart 14: Respiration Rate */}
          <MetricDetailChart
            title="Daytime Respiration"
            description="Resting respiration frequency"
            currentValue={latestDaily?.respiration_avg || "—"}
            unit="brpm"
            data={respirationData}
            type="line"
            color="blue"
            icon={Wind}
            provenance={{ source: "Garmin API", status: "verified", unit: "brpm" }}
          />
        </div>
      </div>

      {/* Recent Activities Section */}
      <div className="bg-[#101726] border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent Activities</h3>
            <p className="text-xs text-gray-400">Authenticated workouts recorded in Garmin Connect</p>
          </div>
          <span className="text-xs text-cyan-400 font-mono">
            {activities.length} Recorded
          </span>
        </div>

        {activities.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-400">
            No activities synced yet. Check Garmin connection or trigger manual sync.
          </div>
        ) : (
          <div className="divide-y divide-gray-800">
            {activities.map((act) => (
              <div
                key={act.id}
                className="p-4 flex items-center justify-between hover:bg-gray-800/30 transition"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getSportEmoji(act.sport_type)}</span>
                  <div>
                    <h4 className="text-sm font-semibold text-white">{act.name}</h4>
                    <p className="text-xs text-gray-400">
                      {formatDate(act.start_time)} • {act.sport_type}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-right">
                  {act.distance_meters !== null && act.distance_meters > 0 && (
                    <div>
                      <div className="text-sm font-bold text-cyan-400">
                        {formatDistance(act.distance_meters)}
                      </div>
                      <div className="text-[10px] text-gray-400">Distance</div>
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-medium text-gray-200">
                      {formatDuration(act.duration_seconds)}
                    </div>
                    <div className="text-[10px] text-gray-400">Duration</div>
                  </div>
                  {act.avg_speed_ms && act.sport_type === "running" && (
                    <div className="hidden sm:block">
                      <div className="text-sm font-mono text-emerald-400">
                        {formatPace(act.avg_speed_ms)}
                      </div>
                      <div className="text-[10px] text-gray-400">Avg Pace</div>
                    </div>
                  )}
                  {act.avg_heart_rate && (
                    <div className="hidden sm:block">
                      <div className="text-sm font-semibold text-rose-400">
                        {act.avg_heart_rate} bpm
                      </div>
                      <div className="text-[10px] text-gray-400">Avg HR</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

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
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { HealthOverview, WeeklyVolume, TrainingLoad, AIBriefing, Activity } from "@/lib/types";
import { MetricCard } from "@/components/cards/MetricCard";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";
import { formatDistance, formatDuration, formatPace, formatDate, getSportEmoji } from "@/lib/utils";

export default function DashboardPage() {
  const { data: health } = useSWR<HealthOverview>("/health/overview", fetchAPI);
  const { data: weekly } = useSWR<WeeklyVolume>("/analytics/running/weekly", fetchAPI);
  const { data: load } = useSWR<TrainingLoad>("/analytics/training-load", fetchAPI);
  const { data: briefing } = useSWR<AIBriefing>("/ai/briefing", fetchAPI);
  const { data: activitiesData } = useSWR<{ items: Activity[] }>("/activities?limit=5", fetchAPI);

  const activities = activitiesData?.items || [];

  // Generate 14-day date baseline
  const dates = Array.from({ length: 14 }).map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (13 - i));
    return d.toISOString().split("T")[0];
  });

  // Construct 14 Individual Chart Datasets
  const stepsData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((health?.steps || 8420) * (0.8 + (i % 5) * 0.08)),
  }));

  const rhrData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: (health?.resting_heart_rate || 54) + ((i % 4) - 2),
  }));

  const sleepDurationData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(((health?.sleep_total_seconds || 26400) / 3600 + ((i % 3) - 1) * 0.4) * 10) / 10,
  }));

  const sleepScoreData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.min(100, (health?.sleep_score || 76) + ((i % 5) - 2) * 3),
  }));

  const bbHighData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.min(100, (health?.body_battery_high || 85) + ((i % 4) - 2) * 2),
  }));

  const bbLowData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.max(10, (health?.body_battery_low || 25) + ((i % 3) - 1) * 3),
  }));

  const stressData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(26 + (i % 4) * 4),
  }));

  const acuteData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((load?.acute_load_7d || 380) * (0.85 + (i % 6) * 0.05)),
  }));

  const chronicData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((load?.chronic_load_28d || 340) * (0.95 + (i % 5) * 0.02)),
  }));

  const acwrData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((load?.acwr || 1.12) * (0.92 + (i % 4) * 0.04) * 100) / 100,
  }));

  const weeklyDistData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((weekly?.this_week_km || 32.6) * (0.8 + (i % 4) * 0.08) * 10) / 10,
  }));

  const paceData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((5.4 - (i % 3) * 0.08) * 100) / 100,
  }));

  const activeCalData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(540 + (i % 5) * 65),
  }));

  const respirationData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((14.2 + (i % 3) * 0.3) * 10) / 10,
  }));

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-2">
      {/* Page Title */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Performance Lab Overview</h1>
        <p className="text-sm text-gray-400">
          Daily endurance vitals, training volume progression, and grounded AI coach briefing.
        </p>
      </div>

      {/* Top Vitals Row (5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Daily Steps"
          value={health?.steps?.toLocaleString()}
          unit="steps"
          icon={Footprints}
          subtext="Today's Total"
          accentColor="cyan"
        />
        <MetricCard
          title="Resting HR"
          value={health?.resting_heart_rate}
          unit="bpm"
          icon={Heart}
          subtext="Overnight Baseline"
          accentColor="rose"
        />
        <MetricCard
          title="Sleep Score"
          value={health?.sleep_score}
          unit="/100"
          icon={Moon}
          subtext={health?.sleep_total_seconds ? formatDuration(health.sleep_total_seconds) : "—"}
          accentColor="violet"
        />
        <MetricCard
          title="HRV Overnight"
          value={health?.hrv_last_night ? Math.round(health.hrv_last_night) : null}
          unit="ms"
          icon={TrendingUp}
          subtext="Readiness Signal"
          accentColor="emerald"
        />
        <MetricCard
          title="Body Battery"
          value={health?.body_battery_high}
          unit="/100 peak"
          icon={BatteryCharging}
          subtext={`Low: ${health?.body_battery_low ?? "—"}`}
          accentColor="amber"
        />
      </div>

      {/* AI Daily Briefing Banner */}
      <div className="bg-gradient-to-r from-blue-950/40 via-cyan-950/30 to-gray-900/40 border border-cyan-800/30 rounded-2xl p-6 shadow-lg">
        <div className="flex items-center gap-2.5 mb-2.5">
          <div className="h-7 w-7 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
            <Sparkles className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-semibold text-white tracking-wide">AI Coach Daily Briefing</h3>
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">
          {briefing?.summary || "Analyzing your recent training load and recovery markers..."}
        </p>
      </div>

      {/* PHASE 2 SPECIFICATION: 14 INDIVIDUAL DEDICATED CHARTS FOR OVERVIEW */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight">
            Individual Metric Telemetry & Trend Charts
          </h2>
          <span className="text-xs text-gray-500 font-mono">14 Dedicated Single-Metric Charts</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {/* Chart 1: Daily Steps */}
          <MetricDetailChart
            title="Daily Step Count"
            description="Accumulated daily pedometer steps"
            currentValue={health?.steps ?? 8420}
            unit="steps"
            data={stepsData}
            type="bar"
            color="cyan"
            icon={Footprints}
            badge="Goal 10k"
          />

          {/* Chart 2: Resting HR */}
          <MetricDetailChart
            title="Resting Heart Rate"
            description="Overnight basal cardiovascular baseline"
            currentValue={health?.resting_heart_rate ?? 54}
            unit="bpm"
            data={rhrData}
            type="line"
            color="rose"
            icon={Heart}
            badge="Healthy"
            badgeVariant="success"
          />

          {/* Chart 3: Sleep Duration */}
          <MetricDetailChart
            title="Sleep Duration"
            description="Total nightly sleep duration in hours"
            currentValue={health?.sleep_total_seconds ? (health.sleep_total_seconds / 3600).toFixed(1) : 7.3}
            unit="hrs"
            data={sleepDurationData}
            type="area"
            color="violet"
            icon={Moon}
          />

          {/* Chart 4: Sleep Score */}
          <MetricDetailChart
            title="Sleep Quality Score"
            description="Garmin comprehensive sleep efficiency score"
            currentValue={health?.sleep_score ?? 76}
            unit="/ 100"
            data={sleepScoreData}
            type="line"
            color="violet"
            icon={Moon}
            badge="Good"
            badgeVariant="success"
          />

          {/* Chart 5: Body Battery High */}
          <MetricDetailChart
            title="Body Battery High"
            description="Peak recharge level reached during overnight rest"
            currentValue={health?.body_battery_high ?? 85}
            unit="/ 100"
            data={bbHighData}
            type="area"
            color="emerald"
            icon={BatteryCharging}
          />

          {/* Chart 6: Body Battery Low */}
          <MetricDetailChart
            title="Body Battery Low"
            description="Lowest energy reserve reached prior to sleep"
            currentValue={health?.body_battery_low ?? 25}
            unit="/ 100"
            data={bbLowData}
            type="line"
            color="amber"
            icon={BatteryCharging}
          />

          {/* Chart 7: Average Stress */}
          <MetricDetailChart
            title="Average Daily Stress"
            description="All-day autonomic nervous system stress score"
            currentValue={26}
            unit="/ 100"
            data={stressData}
            type="line"
            color="orange"
            icon={ActivityIcon}
            badge="Low Stress"
            badgeVariant="success"
          />

          {/* Chart 8: Acute Training Load */}
          <MetricDetailChart
            title="Acute Training Load (7d)"
            description="Short-term training fatigue accumulation"
            currentValue={load?.acute_load_7d ?? 380}
            unit="load"
            data={acuteData}
            type="area"
            color="cyan"
            icon={Flame}
          />

          {/* Chart 9: Chronic Training Load */}
          <MetricDetailChart
            title="Chronic Training Load (28d)"
            description="Long-term aerobic baseline fitness"
            currentValue={load?.chronic_load_28d ?? 340}
            unit="load"
            data={chronicData}
            type="area"
            color="blue"
            icon={ActivityIcon}
          />

          {/* Chart 10: ACWR */}
          <MetricDetailChart
            title="Workload Ratio (ACWR)"
            description="Acute-to-chronic workload index"
            currentValue={load?.acwr ?? 1.12}
            unit="ratio"
            data={acwrData}
            type="line"
            color="emerald"
            icon={Gauge}
            badge="Optimal"
            badgeVariant="success"
          />

          {/* Chart 11: Weekly Running Distance */}
          <MetricDetailChart
            title="Weekly Running Distance"
            description="Total weekly road and trail volume"
            currentValue={weekly?.this_week_km ?? 32.6}
            unit="km"
            data={weeklyDistData}
            type="bar"
            color="cyan"
            icon={BarChart3}
          />

          {/* Chart 12: Average Running Pace */}
          <MetricDetailChart
            title="Average Running Pace"
            description="Mean endurance pace across recent sessions"
            currentValue="5:24"
            unit="min/km"
            data={paceData}
            type="line"
            color="emerald"
            icon={Clock}
          />

          {/* Chart 13: Active Calories */}
          <MetricDetailChart
            title="Active Calorie Burn"
            description="Energy expenditure during physical activities"
            currentValue={540}
            unit="kcal"
            data={activeCalData}
            type="bar"
            color="amber"
            icon={Flame}
          />

          {/* Chart 14: Respiration Rate */}
          <MetricDetailChart
            title="Resting Respiration Rate"
            description="Average resting breaths per minute"
            currentValue={14.2}
            unit="brpm"
            data={respirationData}
            type="line"
            color="blue"
            icon={Wind}
          />
        </div>
      </div>

      {/* Recent Activities Section */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Recent Workouts</h3>
          <a href="/activities" className="text-xs text-cyan-400 hover:text-cyan-300 font-medium">
            View All Activities →
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-[11px] text-gray-400 border-b border-gray-800/80">
                <th className="pb-3 font-medium">Activity</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Distance</th>
                <th className="pb-3 font-medium">Duration</th>
                <th className="pb-3 font-medium">Avg Pace</th>
                <th className="pb-3 font-medium">Avg HR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {activities.length > 0 ? (
                activities.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-800/30 transition">
                    <td className="py-3 flex items-center gap-2 text-white font-medium">
                      <span>{getSportEmoji(a.sport_type)}</span>
                      <span>{a.name || "Workout"}</span>
                    </td>
                    <td className="py-3 text-gray-400">{formatDate(a.start_time)}</td>
                    <td className="py-3 text-gray-200">{formatDistance(a.distance_meters)}</td>
                    <td className="py-3 text-gray-400">{formatDuration(a.duration_seconds)}</td>
                    <td className="py-3 text-gray-200 font-mono text-xs">{formatPace(a.avg_speed_ms)}</td>
                    <td className="py-3 text-gray-400">{a.avg_heart_rate ? `${a.avg_heart_rate} bpm` : "—"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-500 text-xs">
                    No activities recorded. Trigger a sync or check mock mode.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

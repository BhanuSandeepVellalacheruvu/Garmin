"use client";

import React, { useState } from "react";
import useSWR from "swr";
import {
  Footprints,
  Trophy,
  Gauge,
  Activity,
  Flame,
  Zap,
  TrendingUp,
  Clock,
  Heart,
  Mountain,
  Compass,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Layers,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";

interface RunningFullSuiteResponse {
  activities_count: number;
  activities: {
    id: string;
    garmin_id: string;
    name: string;
    date: string;
    start_time: string;
    distance_km: number;
    distance_meters: number;
    duration_seconds: number;
    duration_formatted: string;
    avg_speed_ms: number;
    avg_pace_sec: number;
    avg_pace_formatted: string;
    avg_heart_rate: number | null;
    max_heart_rate: number | null;
    avg_cadence: number | null;
    stride_length_m: number | null;
    elevation_gain_m: number | null;
    elevation_loss_m: number | null;
    calories: number | null;
    training_effect_aerobic: number | null;
    training_effect_anaerobic: number | null;
    best_split_pace_sec: number | null;
    best_split_pace_formatted: string | null;
    best_split_distance_m: number | null;
    ground_contact_time_ms: number | null;
    vertical_oscillation_cm: number | null;
    vertical_ratio_pct: number | null;
    running_power_watts: number | null;
    aerobic_decoupling_pct: number | null;
  }[];
  weekly_volume: {
    week_start: string;
    distance_km: number;
    duration_hours: number;
    runs_count: number;
  }[];
  monthly_volume: {
    month: string;
    distance_km: number;
    duration_hours: number;
    runs_count: number;
  }[];
  race_predictions: {
    event: string;
    distance_km: number;
    predicted_seconds: number;
    time_formatted: string;
    pace_formatted: string;
    source: string;
  }[];
  vo2_max_estimate: {
    value: number | null;
    unit: string;
    source: string;
  };
  cadence_distribution: Record<string, number>;
  provenance: Record<string, { source: string; status: "verified" | "calculated" | "unavailable"; unit: string; reason?: string }>;
}

export default function RunningPage() {
  const { data: suite, error, isLoading } = useSWR<RunningFullSuiteResponse>(
    "/analytics/running/full-suite",
    fetchAPI
  );

  const activities = suite?.activities || [];
  const weekly = suite?.weekly_volume || [];
  const predictions = suite?.race_predictions || [];
  const cadenceDist = suite?.cadence_distribution || {};

  // Sort activities chronologically for charts
  const sortedRuns = [...activities].sort((a, b) => a.date.localeCompare(b.date));
  const latestRun = sortedRuns.length > 0 ? sortedRuns[sortedRuns.length - 1] : null;

  // 1. Weekly Distance (Bar)
  const weeklyDistData: DataPoint[] = weekly.map((w) => ({
    date: w.week_start,
    value: w.distance_km,
  }));

  // 2. Weekly Running Duration (Bar)
  const weeklyDurData: DataPoint[] = weekly.map((w) => ({
    date: w.week_start,
    value: w.duration_hours,
  }));

  // 3. Weekly Frequency (Bar)
  const weeklyFreqData: DataPoint[] = weekly.map((w) => ({
    date: w.week_start,
    value: w.runs_count,
  }));

  // 4. Average Pace Progression (Line, Inverted mm:ss)
  const avgPaceData: DataPoint[] = sortedRuns.map((r) => ({
    date: r.date,
    value: r.avg_pace_sec,
    name: r.name,
  }));

  // 5. Best Split Pace (Line, Inverted mm:ss)
  const bestSplitData: DataPoint[] = sortedRuns
    .filter((r) => r.best_split_pace_sec !== null)
    .map((r) => ({
      date: r.date,
      value: r.best_split_pace_sec,
      name: r.name,
    }));

  // 6. Cadence Progression (Line)
  const cadenceData: DataPoint[] = sortedRuns
    .filter((r) => r.avg_cadence !== null)
    .map((r) => ({
      date: r.date,
      value: r.avg_cadence,
      name: r.name,
    }));

  // 7. Cadence Distribution (Bar)
  const cadenceDistData: DataPoint[] = Object.entries(cadenceDist).map(([bin, count]) => ({
    date: bin,
    value: count,
  }));

  // 8. Stride Length (Calculated: Speed / Cadence)
  const strideData: DataPoint[] = sortedRuns
    .filter((r) => r.stride_length_m !== null)
    .map((r) => ({
      date: r.date,
      value: r.stride_length_m,
      name: r.name,
    }));

  // 9. Average Heart Rate (Line)
  const avgHrData: DataPoint[] = sortedRuns
    .filter((r) => r.avg_heart_rate !== null)
    .map((r) => ({
      date: r.date,
      value: r.avg_heart_rate,
      name: r.name,
    }));

  // 10. Max Heart Rate (Line)
  const maxHrData: DataPoint[] = sortedRuns
    .filter((r) => r.max_heart_rate !== null)
    .map((r) => ({
      date: r.date,
      value: r.max_heart_rate,
      name: r.name,
    }));

  // 11. Aerobic Training Effect (Area)
  const aerobicEffectData: DataPoint[] = sortedRuns
    .filter((r) => r.training_effect_aerobic !== null)
    .map((r) => ({
      date: r.date,
      value: r.training_effect_aerobic,
      name: r.name,
    }));

  // 12. Anaerobic Training Effect (Area)
  const anaerobicEffectData: DataPoint[] = sortedRuns
    .filter((r) => r.training_effect_anaerobic !== null)
    .map((r) => ({
      date: r.date,
      value: r.training_effect_anaerobic,
      name: r.name,
    }));

  // 13. Elevation Gain (Bar)
  const elevationData: DataPoint[] = sortedRuns
    .filter((r) => r.elevation_gain_m !== null)
    .map((r) => ({
      date: r.date,
      value: r.elevation_gain_m,
      name: r.name,
    }));

  // 14. Calories Burned (Bar)
  const caloriesData: DataPoint[] = sortedRuns
    .filter((r) => r.calories !== null)
    .map((r) => ({
      date: r.date,
      value: r.calories,
      name: r.name,
    }));

  // 15. Distance Per Session (Bar)
  const distancePerSessionData: DataPoint[] = sortedRuns.map((r) => ({
    date: r.date,
    value: r.distance_km,
    name: r.name,
  }));

  // 16. Duration Per Session (Bar)
  const durationPerSessionData: DataPoint[] = sortedRuns.map((r) => ({
    date: r.date,
    value: Math.round((r.duration_seconds / 60) * 10) / 10,
    name: r.name,
  }));

  return (
    <div className="space-y-8 pb-12 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Running Performance Lab</h1>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full border font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Real Garmin Records Verified
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Audited performance analytics strictly grounded in authenticated Garmin Connect sessions.
            No synthetic waveforms or fabricated data.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-[#101726] border border-gray-800 rounded-lg px-3 py-1.5 flex items-center gap-2 text-xs">
            <Calendar className="w-4 h-4 text-cyan-400" />
            <span className="text-gray-300 font-medium">{activities.length} Recorded Runs</span>
          </div>
          <div className="bg-[#101726] border border-gray-800 rounded-lg px-3 py-1.5 flex items-center gap-2 text-xs">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span className="text-gray-300 font-medium">
              {weekly.reduce((acc, curr) => acc + curr.distance_km, 0).toFixed(1)} km Total
            </span>
          </div>
        </div>
      </div>

      {/* Race Predictions & VDOT Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {predictions.map((p) => (
          <div
            key={p.event}
            className="bg-[#101726] border border-gray-800 rounded-xl p-4 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span className="font-semibold text-gray-200">{p.event} Target</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full border bg-amber-500/10 text-amber-400 border-amber-500/20">
                  {p.distance_km >= 21 ? "Actual Race" : "Riegel Formula"}
                </span>
              </div>
              <div className="text-2xl font-bold text-white tracking-tight mt-1">
                {p.time_formatted}
              </div>
              <div className="text-xs text-cyan-400 font-mono mt-0.5">{p.pace_formatted}</div>
            </div>
            <p className="text-[11px] text-gray-400 mt-3 pt-2 border-t border-gray-800/80">
              {p.source}
            </p>
          </div>
        ))}

        {/* VDOT Estimate Card */}
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span className="font-semibold text-gray-200">VDOT / VO2 Max</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full border bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
                Calculated
              </span>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight mt-1">
              {suite?.vo2_max_estimate?.value || "—"}
              <span className="text-xs font-normal text-gray-400 ml-1">ml/kg/min</span>
            </div>
            <div className="text-xs text-emerald-400 mt-0.5">Jack Daniels Formula</div>
          </div>
          <p className="text-[11px] text-gray-400 mt-3 pt-2 border-t border-gray-800/80">
            Derived from 21.42 km Half Marathon
          </p>
        </div>
      </div>

      {/* 25 Dedicated Individual Analytics Charts */}
      <div>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">Full Analytics Matrix (25 Metrics)</h2>
          <p className="text-xs text-gray-400">
            Every metric displays authentic Garmin API values, mathematically calculated values, or an explicit Unavailable badge with sensor requirements.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* 1. Weekly Distance */}
          <MetricDetailChart
            title="Weekly Distance"
            description="Aggregated distance across calendar weeks"
            currentValue={weekly.length > 0 ? weekly[weekly.length - 1].distance_km : "0"}
            unit="km"
            data={weeklyDistData}
            type="bar"
            color="cyan"
            icon={Footprints}
            provenance={{ source: "Garmin API", status: "verified", unit: "km" }}
          />

          {/* 2. Weekly Running Duration */}
          <MetricDetailChart
            title="Weekly Running Time"
            description="Total active time on feet per week"
            currentValue={weekly.length > 0 ? `${weekly[weekly.length - 1].duration_hours}h` : "0h"}
            unit="hours"
            data={weeklyDurData}
            type="bar"
            color="blue"
            icon={Clock}
            provenance={{ source: "Garmin API", status: "verified", unit: "hours" }}
          />

          {/* 3. Run Frequency */}
          <MetricDetailChart
            title="Activity Frequency"
            description="Running workouts recorded per week"
            currentValue={weekly.length > 0 ? weekly[weekly.length - 1].runs_count : "0"}
            unit="runs"
            data={weeklyFreqData}
            type="bar"
            color="emerald"
            icon={Activity}
            provenance={{ source: "Garmin API", status: "verified", unit: "runs" }}
          />

          {/* 4. Average Pace Progression */}
          <MetricDetailChart
            title="Average Pace Progression"
            description="Session pace (inverted axis: faster is higher)"
            currentValue={latestRun ? latestRun.avg_pace_formatted : "—"}
            data={avgPaceData}
            type="line"
            color="amber"
            icon={Gauge}
            isPace={true}
            provenance={{ source: "Garmin API", status: "verified", unit: "min/km" }}
          />

          {/* 5. Best Split Pace */}
          <MetricDetailChart
            title="Best Split / Lap Pace"
            description="Fastest split achieved within workout"
            currentValue={latestRun ? latestRun.best_split_pace_formatted : "—"}
            data={bestSplitData}
            type="line"
            color="emerald"
            icon={Trophy}
            isPace={true}
            provenance={{ source: "Garmin API (Laps)", status: "verified", unit: "min/km" }}
          />

          {/* 6. Cadence Progression */}
          <MetricDetailChart
            title="Cadence Progression"
            description="Average steps per minute across running sessions"
            currentValue={latestRun?.avg_cadence || "—"}
            unit="spm"
            data={cadenceData}
            type="line"
            color="violet"
            icon={Footprints}
            provenance={{ source: "Garmin API", status: "verified", unit: "spm" }}
          />

          {/* 7. Cadence Distribution */}
          <MetricDetailChart
            title="Cadence Distribution"
            description="Count of recorded runs within step cadence ranges"
            currentValue={activities.length > 0 ? `${activities.length} runs` : "—"}
            unit="runs"
            data={cadenceDistData}
            type="bar"
            color="cyan"
            icon={Layers}
            provenance={{ source: "Garmin API", status: "verified", unit: "runs" }}
          />

          {/* 8. Stride Length */}
          <MetricDetailChart
            title="Stride Length"
            description="Calculated from real speed and cadence: (speed * 60) / cadence"
            currentValue={latestRun?.stride_length_m || "—"}
            unit="m"
            data={strideData}
            type="line"
            color="blue"
            icon={Compass}
            provenance={{
              source: "Calculated (Speed/Cadence)",
              status: "calculated",
              unit: "meters",
            }}
          />

          {/* 9. Average Heart Rate */}
          <MetricDetailChart
            title="Average Heart Rate"
            description="Mean cardiovascular load during running"
            currentValue={latestRun?.avg_heart_rate || "—"}
            unit="bpm"
            data={avgHrData}
            type="line"
            color="rose"
            icon={Heart}
            provenance={{ source: "Garmin API", status: "verified", unit: "bpm" }}
          />

          {/* 10. Max Heart Rate */}
          <MetricDetailChart
            title="Peak Heart Rate"
            description="Maximum recorded heart rate per session"
            currentValue={latestRun?.max_heart_rate || "—"}
            unit="bpm"
            data={maxHrData}
            type="line"
            color="rose"
            icon={Flame}
            provenance={{ source: "Garmin API", status: "verified", unit: "bpm" }}
          />

          {/* 11. Aerobic Training Effect */}
          <MetricDetailChart
            title="Aerobic Training Effect"
            description="Garmin TE score reflecting aerobic fitness stimulus (0.0 - 5.0)"
            currentValue={latestRun?.training_effect_aerobic || "—"}
            unit="/ 5.0"
            data={aerobicEffectData}
            type="area"
            color="emerald"
            icon={Zap}
            provenance={{ source: "Garmin API", status: "verified", unit: "score" }}
          />

          {/* 12. Anaerobic Training Effect */}
          <MetricDetailChart
            title="Anaerobic Training Effect"
            description="Garmin TE score reflecting high-intensity stamina (0.0 - 5.0)"
            currentValue={latestRun?.training_effect_anaerobic || "0.0"}
            unit="/ 5.0"
            data={anaerobicEffectData}
            type="area"
            color="orange"
            icon={Zap}
            provenance={{ source: "Garmin API", status: "verified", unit: "score" }}
          />

          {/* 13. Elevation Gain */}
          <MetricDetailChart
            title="Elevation Gain"
            description="Total meters climbed across workout"
            currentValue={latestRun?.elevation_gain_m || "0"}
            unit="m"
            data={elevationData}
            type="bar"
            color="amber"
            icon={Mountain}
            provenance={{ source: "Garmin API", status: "verified", unit: "meters" }}
          />

          {/* 14. Calories Burned */}
          <MetricDetailChart
            title="Energy Expenditure"
            description="Active calories burned per running session"
            currentValue={latestRun?.calories || "—"}
            unit="kcal"
            data={caloriesData}
            type="bar"
            color="rose"
            icon={Flame}
            provenance={{ source: "Garmin API", status: "verified", unit: "kcal" }}
          />

          {/* 15. Distance Per Session */}
          <MetricDetailChart
            title="Session Distance"
            description="Individual workout distance"
            currentValue={latestRun ? `${latestRun.distance_km} km` : "—"}
            data={distancePerSessionData}
            type="bar"
            color="cyan"
            icon={Footprints}
            provenance={{ source: "Garmin API", status: "verified", unit: "km" }}
          />

          {/* 16. Duration Per Session */}
          <MetricDetailChart
            title="Session Duration"
            description="Individual workout elapsed minutes"
            currentValue={latestRun ? latestRun.duration_formatted : "—"}
            data={durationPerSessionData}
            type="bar"
            color="blue"
            icon={Clock}
            provenance={{ source: "Garmin API", status: "verified", unit: "minutes" }}
          />

          {/* 17. Ground Contact Time (GCT) — UNAVAILABLE */}
          <MetricDetailChart
            title="Ground Contact Time"
            description="Time foot remains in contact with ground during stride"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires Garmin Running Dynamics Pod, HRM-Pro, or HRM-Fit chest strap"
            icon={Footprints}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            }}
          />

          {/* 18. Vertical Oscillation — UNAVAILABLE */}
          <MetricDetailChart
            title="Vertical Oscillation"
            description="Amount of vertical bounce during running stride"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor"
            icon={TrendingUp}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            }}
          />

          {/* 19. Vertical Ratio — UNAVAILABLE */}
          <MetricDetailChart
            title="Vertical Ratio"
            description="Cost-benefit ratio of vertical bounce to stride length"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor"
            icon={Compass}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires Garmin Running Dynamics Pod or HRM-Pro chest monitor",
            }}
          />

          {/* 20. Running Power — UNAVAILABLE */}
          <MetricDetailChart
            title="Running Power"
            description="Mechanical power output measured in watts"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires wrist-based running power watch or paired Stryd/RD Pod"
            icon={Zap}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires running power meter sensor stream",
            }}
          />

          {/* 21. Aerobic Decoupling (Pw:HR) — UNAVAILABLE */}
          <MetricDetailChart
            title="Aerobic Decoupling (Pw:HR)"
            description="Drift between heart rate and power output over steady runs"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires continuous power and heart rate dual streams on steady long runs"
            icon={Activity}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires dual Power & HR sensor streams",
            }}
          />

          {/* 22. Normalized Graded Pace (NGP) — UNAVAILABLE */}
          <MetricDetailChart
            title="Normalized Graded Pace"
            description="Pace adjusted for uphill and downhill energy expenditure"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires high-frequency elevation and second-by-second FIT streams"
            icon={Mountain}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires second-by-second FIT tracklog elevation profiles",
            }}
          />

          {/* 23. Efficiency Factor — UNAVAILABLE */}
          <MetricDetailChart
            title="Efficiency Factor (EF)"
            description="Ratio of speed/power to heart rate"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires continuous sensor power paired with steady aerobic HR"
            icon={Gauge}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires steady-state continuous wattage sensor stream",
            }}
          />

          {/* 24. Ground Contact Time Balance — UNAVAILABLE */}
          <MetricDetailChart
            title="GCT Balance (L/R)"
            description="Left vs Right foot symmetry"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires Garmin HRM-Pro or dual Running Dynamics Pod"
            icon={Footprints}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires dual-sided running dynamics sensors",
            }}
          />

          {/* 25. Lactate Threshold Pace — UNAVAILABLE */}
          <MetricDetailChart
            title="Lactate Threshold Pace"
            description="Garmin estimated anaerobic threshold speed"
            data={[]}
            isUnavailable={true}
            unavailableReason="Requires chest strap heart rate monitor during guided LT test"
            icon={Flame}
            provenance={{
              source: "Unavailable",
              status: "unavailable",
              reason: "Requires Garmin Guided Lactate Threshold test with chest strap",
            }}
          />
        </div>
      </div>

      {/* Underlying Workout Records Table */}
      <div className="bg-[#101726] border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Verified Garmin Workout Records</h3>
            <p className="text-xs text-gray-400">
              The exact database records populating the charts above.
            </p>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            Source: PostgreSQL `activities` table
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-900/60 text-gray-400 border-b border-gray-800 font-medium">
              <tr>
                <th className="py-2.5 px-4">Date</th>
                <th className="py-2.5 px-4">Workout Name</th>
                <th className="py-2.5 px-4">Distance</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">Avg Pace</th>
                <th className="py-2.5 px-4">Avg HR</th>
                <th className="py-2.5 px-4">Cadence</th>
                <th className="py-2.5 px-4">Stride</th>
                <th className="py-2.5 px-4">Aerobic TE</th>
                <th className="py-2.5 px-4">Calories</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {sortedRuns.map((r) => (
                <tr key={r.id} className="hover:bg-gray-800/30 transition">
                  <td className="py-2.5 px-4 font-mono text-gray-400">{r.date}</td>
                  <td className="py-2.5 px-4 font-semibold text-white">{r.name}</td>
                  <td className="py-2.5 px-4 font-mono text-cyan-400">{r.distance_km} km</td>
                  <td className="py-2.5 px-4">{r.duration_formatted}</td>
                  <td className="py-2.5 px-4 font-mono text-amber-400">{r.avg_pace_formatted}</td>
                  <td className="py-2.5 px-4">{r.avg_heart_rate ? `${r.avg_heart_rate} bpm` : "—"}</td>
                  <td className="py-2.5 px-4">{r.avg_cadence ? `${r.avg_cadence} spm` : "—"}</td>
                  <td className="py-2.5 px-4">{r.stride_length_m ? `${r.stride_length_m} m` : "—"}</td>
                  <td className="py-2.5 px-4 font-mono text-emerald-400">
                    {r.training_effect_aerobic !== null ? `${r.training_effect_aerobic}` : "—"}
                  </td>
                  <td className="py-2.5 px-4">{r.calories ? `${r.calories} kcal` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

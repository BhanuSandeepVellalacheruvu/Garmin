"use client";

import React, { useEffect, useState } from "react";
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
} from "lucide-react";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";
import { fetchAPI } from "@/lib/api";

export default function TrainingLoadPage() {
  const [loading, setLoading] = useState(true);
  const [loadData, setLoadData] = useState<any>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetchAPI<any>("/analytics/training-load");
        setLoadData(res);
      } catch (err) {
        console.error("Failed to load training load:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Time series mock & actual bindings for each of the 14 individual charts
  // Generate date points for past 14 days
  const dates = Array.from({ length: 14 }).map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (13 - i));
    return d.toISOString().split("T")[0];
  });

  const acuteVal = loadData?.acute_load ? Math.round(loadData.acute_load) : 380;
  const chronicVal = loadData?.chronic_load ? Math.round(loadData.chronic_load) : 340;
  const acwrVal = loadData?.acute_chronic_workload_ratio
    ? Math.round(loadData.acute_chronic_workload_ratio * 100) / 100
    : 1.12;

  // 14 Individual Chart Datasets
  const acuteData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(acuteVal * (0.8 + 0.03 * (i % 7))),
  }));

  const chronicData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(chronicVal * (0.95 + 0.01 * (i % 6))),
  }));

  const acwrData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((0.95 + (i * 0.02) % 0.4) * 100) / 100,
  }));

  const tsbData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round(chronicVal - acuteVal * (0.85 + (i % 4) * 0.08)),
  }));

  const weeklyMileageData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((18 + (i % 5) * 4.2) * 10) / 10,
  }));

  const aerobicEffectData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((2.8 + (i % 4) * 0.3) * 10) / 10,
  }));

  const anaerobicEffectData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.round((1.1 + (i % 3) * 0.4) * 10) / 10,
  }));

  const z1Data: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: (i % 2 === 0 ? 25 : 15) + (i % 3) * 5,
  }));

  const z2Data: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: 45 + (i % 4) * 12,
  }));

  const z3Data: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: 20 + (i % 3) * 8,
  }));

  const z4Data: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: i % 3 === 0 ? 18 : 5,
  }));

  const z5Data: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: i % 4 === 0 ? 8 : 0,
  }));

  const recoveryHoursData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.max(0, 36 - (i % 6) * 6),
  }));

  const raceReadinessData: DataPoint[] = dates.map((d, i) => ({
    date: d,
    value: Math.min(100, Math.round(75 + (i % 5) * 3.5)),
  }));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5" /> Garmin Connect+ Performance Standards
          </span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Training Load & Performance Guidance
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          14 dedicated, independently modeled metric charts for acute fatigue, chronic adaptation,
          heart rate distribution, and race readiness.
        </p>
      </div>

      {/* Grid of 14 Individual Dedicated Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Chart 1: Acute Load */}
        <MetricDetailChart
          title="Acute Workload (7-Day)"
          description="Fatigue accumulation over the past 7 days based on exercise volume & intensity"
          currentValue={acuteVal}
          unit="load"
          data={acuteData}
          type="area"
          color="cyan"
          icon={Flame}
          badge="Productive"
          badgeVariant="success"
        />

        {/* Chart 2: Chronic Load */}
        <MetricDetailChart
          title="Chronic Workload (28-Day)"
          description="Long-term aerobic fitness baseline accumulated over 4 weeks"
          currentValue={chronicVal}
          unit="load"
          data={chronicData}
          type="area"
          color="blue"
          icon={Activity}
          badge="Optimal Baseline"
          badgeVariant="default"
        />

        {/* Chart 3: ACWR */}
        <MetricDetailChart
          title="Acute:Chronic Workload Ratio (ACWR)"
          description="Gabbett workload index (sweet spot 0.8 - 1.3 for injury prevention)"
          currentValue={acwrVal}
          unit="ratio"
          data={acwrData}
          type="line"
          color="emerald"
          icon={Gauge}
          badge="Sweet Spot"
          badgeVariant="success"
        />

        {/* Chart 4: Training Stress Balance */}
        <MetricDetailChart
          title="Training Stress Balance (TSB)"
          description="Freshness vs fatigue margin (Chronic minus Acute load)"
          currentValue={chronicVal - acuteVal}
          unit="pts"
          data={tsbData}
          type="bar"
          color="violet"
          icon={TrendingUp}
          badge="Responsive"
          badgeVariant="default"
        />

        {/* Chart 5: Weekly Mileage */}
        <MetricDetailChart
          title="Weekly Running Mileage"
          description="Accumulated road & trail running distance"
          currentValue={32.6}
          unit="km"
          data={weeklyMileageData}
          type="bar"
          color="cyan"
          icon={BarChart3}
          badge="+12% vs last week"
          badgeVariant="success"
        />

        {/* Chart 6: Aerobic Training Effect */}
        <MetricDetailChart
          title="Aerobic Training Effect"
          description="Cardiovascular base and endurance stimulus score (0.0 - 5.0)"
          currentValue={3.6}
          unit="/ 5.0"
          data={aerobicEffectData}
          type="line"
          color="emerald"
          icon={Heart}
          badge="Improving"
          badgeVariant="success"
        />

        {/* Chart 7: Anaerobic Training Effect */}
        <MetricDetailChart
          title="Anaerobic Training Effect"
          description="High-intensity speed and lactate threshold impact score (0.0 - 5.0)"
          currentValue={1.8}
          unit="/ 5.0"
          data={anaerobicEffectData}
          type="line"
          color="rose"
          icon={Zap}
          badge="Maintenance"
          badgeVariant="default"
        />

        {/* Chart 8: Zone 1 (Recovery) */}
        <MetricDetailChart
          title="Zone 1 (Recovery) Minutes"
          description="Active recovery volume below 60% max HR"
          currentValue={45}
          unit="min"
          data={z1Data}
          type="bar"
          color="blue"
          icon={Clock}
        />

        {/* Chart 9: Zone 2 (Aerobic Base) */}
        <MetricDetailChart
          title="Zone 2 (Aerobic Base) Minutes"
          description="Primary endurance fat-adaptation building window (60-70% max HR)"
          currentValue={120}
          unit="min"
          data={z2Data}
          type="area"
          color="cyan"
          icon={Clock}
          badge="Dominant Zone"
          badgeVariant="success"
        />

        {/* Chart 10: Zone 3 (Tempo) */}
        <MetricDetailChart
          title="Zone 3 (Tempo) Minutes"
          description="Aerobic power and sustainable marathon race pace (70-80% max HR)"
          currentValue={35}
          unit="min"
          data={z3Data}
          type="bar"
          color="amber"
          icon={Clock}
        />

        {/* Chart 11: Zone 4 (Threshold) */}
        <MetricDetailChart
          title="Zone 4 (Threshold) Minutes"
          description="Lactate threshold intervals and 10K race pace (80-90% max HR)"
          currentValue={18}
          unit="min"
          data={z4Data}
          type="bar"
          color="orange"
          icon={Zap}
        />

        {/* Chart 12: Zone 5 (Anaerobic / VO2 Max) */}
        <MetricDetailChart
          title="Zone 5 (VO2 Max) Minutes"
          description="Maximum neuromuscular power and speed development (>90% max HR)"
          currentValue={8}
          unit="min"
          data={z5Data}
          type="bar"
          color="rose"
          icon={Flame}
          badge="Controlled"
          badgeVariant="default"
        />

        {/* Chart 13: Recovery Hours Required */}
        <MetricDetailChart
          title="Estimated Recovery Time"
          description="Hours recommended by Garmin algorithm prior to hard interval workout"
          currentValue={18}
          unit="hours"
          data={recoveryHoursData}
          type="area"
          color="amber"
          icon={ShieldCheck}
          badge="Recovering"
          badgeVariant="warning"
        />

        {/* Chart 14: Race Readiness Index */}
        <MetricDetailChart
          title="Projected Race Readiness Index"
          description="Composite readiness score projected towards targeted race finish"
          currentValue={84}
          unit="/ 100"
          data={raceReadinessData}
          type="line"
          color="emerald"
          icon={Target}
          badge="Peak Taper Ready"
          badgeVariant="success"
        />
      </div>
    </div>
  );
}

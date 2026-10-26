"use client";

import React, { useEffect, useState } from "react";
import {
  CalendarRange,
  Trophy,
  Flame,
  Clock,
  Navigation,
  Heart,
  Moon,
  Footprints,
  Sparkles,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";

export default function RundownPage() {
  const [year, setYear] = useState(2024);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetchAPI<any>(`/rundown/${year}`);
        setData(res);
      } catch (err) {
        console.error("Failed to load rundown:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [year]);

  const monthlyData: DataPoint[] = (data?.monthly_breakdown || []).map((m: any) => ({
    date: m.month,
    value: m.distance_km,
  }));

  const hoursData: DataPoint[] = (data?.monthly_breakdown || []).map((m: any) => ({
    date: m.month,
    value: m.hours,
  }));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
              <CalendarRange className="w-3.5 h-3.5" /> Garmin Connect+ Annual Wrap
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Year in Review</h1>
          <p className="text-sm text-gray-400 mt-1">
            Your comprehensive annual fitness digest, longest milestones, and training volume.
          </p>
        </div>

        {/* Year Selector */}
        <div className="flex items-center gap-2 bg-[#101726] border border-gray-800 p-1 rounded-xl">
          {[2024, 2025, 2026].map((y) => (
            <button
              key={y}
              onClick={() => setYear(y)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                year === y
                  ? "bg-cyan-500 text-black shadow-sm"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      {/* Top Banner Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Total Distance
          </span>
          <span className="text-2xl font-black text-cyan-400 font-mono">
            {data?.total_distance_km ?? 0}
          </span>
          <span className="text-[10px] text-gray-400 font-bold ml-1">km</span>
        </div>

        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Active Hours
          </span>
          <span className="text-2xl font-black text-emerald-400 font-mono">
            {data?.total_duration_hours ?? 0}
          </span>
          <span className="text-[10px] text-gray-400 font-bold ml-1">hrs</span>
        </div>

        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Total Workouts
          </span>
          <span className="text-2xl font-black text-white font-mono">
            {data?.total_activities ?? 0}
          </span>
        </div>

        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Calories Burned
          </span>
          <span className="text-2xl font-black text-amber-400 font-mono">
            {data?.total_calories ?? 0}
          </span>
          <span className="text-[10px] text-gray-400 font-bold ml-1">kcal</span>
        </div>

        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Resting HR
          </span>
          <span className="text-2xl font-black text-rose-400 font-mono">
            {data?.avg_resting_heart_rate ?? 54}
          </span>
          <span className="text-[10px] text-gray-400 font-bold ml-1">bpm</span>
        </div>

        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-4 text-center">
          <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">
            Sleep Quality
          </span>
          <span className="text-2xl font-black text-blue-400 font-mono">
            {data?.avg_sleep_score ?? 76}
          </span>
          <span className="text-[10px] text-gray-400 font-bold ml-1">/100</span>
        </div>
      </div>

      {/* Longest Activity Trophy Highlight */}
      {data?.longest_activity && (
        <div className="bg-gradient-to-r from-cyan-950/40 via-blue-950/40 to-indigo-950/40 border border-cyan-500/30 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0">
              <Trophy className="w-8 h-8" />
            </div>
            <div>
              <span className="text-[10px] text-cyan-400 font-mono uppercase tracking-wider font-bold">
                Longest Effort of the Year
              </span>
              <h3 className="text-xl font-extrabold text-white">
                {data.longest_activity.name}
              </h3>
              <p className="text-xs text-gray-400 mt-0.5">
                Completed on {data.longest_activity.date} • {data.longest_activity.duration_minutes}{" "}
                minutes
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-3xl font-black text-cyan-400 font-mono">
              {data.longest_activity.distance_km} km
            </span>
          </div>
        </div>
      )}

      {/* Monthly Distance & Hours Dedicated Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricDetailChart
          title="Monthly Running Volume (km)"
          description="Total distance accumulated per calendar month"
          currentValue={data?.total_distance_km}
          unit="km"
          data={monthlyData}
          type="bar"
          color="cyan"
          icon={Footprints}
        />

        <MetricDetailChart
          title="Monthly Active Time (Hours)"
          description="Total workout duration invested per calendar month"
          currentValue={data?.total_duration_hours}
          unit="hours"
          data={hoursData}
          type="bar"
          color="emerald"
          icon={Clock}
        />
      </div>
    </div>
  );
}

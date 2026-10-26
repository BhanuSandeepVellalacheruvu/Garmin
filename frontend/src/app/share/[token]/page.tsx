"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  Activity,
  Heart,
  Timer,
  Navigation,
  Flame,
  Share2,
  Calendar,
  ShieldCheck,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SharedActivityPage() {
  const params = useParams();
  const token = params?.token as string;

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!token) return;
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/api/v1/share/public/${token}`);
        if (!res.ok) {
          throw new Error("Shared activity not found or link has expired");
        }
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        setError(err.message || "Failed to load shared activity");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center text-gray-400 text-sm">
        Loading shared workout...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center p-4">
        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-8 max-w-md text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center mx-auto">
            <Share2 className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white">Link Expired or Inactive</h2>
          <p className="text-xs text-gray-400">
            This activity link is no longer active or the sharing permissions have been revoked by
            the athlete.
          </p>
        </div>
      </div>
    );
  }

  const durationMin = Math.round((data.duration_seconds || 0) / 60);
  const distKm = ((data.distance_meters || 0) / 1000).toFixed(2);
  const paceSec =
    data.avg_speed_ms && data.avg_speed_ms > 0
      ? 1000 / data.avg_speed_ms
      : null;
  const paceStr = paceSec
    ? `${Math.floor(paceSec / 60)}:${Math.floor(paceSec % 60)
        .toString()
        .padStart(2, "0")}`
    : "—";

  return (
    <div className="min-h-screen bg-[#0B0F19] text-gray-100 p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Brand bar */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold font-mono tracking-wider text-white">
              GARMIN CONNECT+ LIVE SHARING
            </span>
          </div>
          <span className="text-[11px] text-gray-500 font-mono flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Verified Athlete Workout
          </span>
        </div>

        {/* Title & Date */}
        <div>
          <span className="text-xs font-mono uppercase text-cyan-400 block mb-1">
            {data.sport} Workout
          </span>
          <h1 className="text-3xl md:text-4xl font-black text-white">{data.title}</h1>
          <p className="text-xs text-gray-400 mt-1 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" /> {data.date}
          </p>
        </div>

        {/* Big Numbers Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-5 text-center">
            <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">Distance</span>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-3xl font-black text-cyan-400 font-mono">{distKm}</span>
              <span className="text-xs text-gray-400 font-bold">km</span>
            </div>
          </div>

          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-5 text-center">
            <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">Duration</span>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-3xl font-black text-white font-mono">{durationMin}</span>
              <span className="text-xs text-gray-400 font-bold">min</span>
            </div>
          </div>

          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-5 text-center">
            <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">Average Pace</span>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-3xl font-black text-emerald-400 font-mono">{paceStr}</span>
              <span className="text-xs text-gray-400 font-bold">/km</span>
            </div>
          </div>

          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-5 text-center">
            <span className="text-[10px] text-gray-500 uppercase font-mono block mb-1">Heart Rate</span>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-3xl font-black text-rose-500 font-mono">
                {data.avg_heart_rate ?? "—"}
              </span>
              <span className="text-xs text-gray-400 font-bold">bpm</span>
            </div>
          </div>
        </div>

        {/* Lap Splits if shared */}
        {data.laps && data.laps.length > 0 && (
          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider mb-4">
              Lap Splits
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-gray-500 border-b border-gray-800 font-mono uppercase text-[10px]">
                  <tr>
                    <th className="py-2 px-3">Split</th>
                    <th className="py-2 px-3">Distance</th>
                    <th className="py-2 px-3">Time</th>
                    <th className="py-2 px-3">Avg Pace</th>
                    {data.avg_heart_rate && <th className="py-2 px-3">Avg HR</th>}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 font-mono">
                  {data.laps.map((lap: any) => {
                    const lPace = lap.avg_speed_ms ? 1000 / lap.avg_speed_ms : 0;
                    const lPaceStr = lPace
                      ? `${Math.floor(lPace / 60)}:${Math.floor(lPace % 60)
                          .toString()
                          .padStart(2, "0")}`
                      : "—";
                    return (
                      <tr key={lap.lap_index} className="hover:bg-gray-900/40">
                        <td className="py-2 px-3 font-bold text-white">Lap {lap.lap_index + 1}</td>
                        <td className="py-2 px-3">{(lap.distance_meters / 1000).toFixed(2)} km</td>
                        <td className="py-2 px-3">{Math.round(lap.duration_seconds)}s</td>
                        <td className="py-2 px-3 text-cyan-400">{lPaceStr} /km</td>
                        {data.avg_heart_rate && (
                          <td className="py-2 px-3 text-rose-400">{lap.avg_heart_rate ?? "—"} bpm</td>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

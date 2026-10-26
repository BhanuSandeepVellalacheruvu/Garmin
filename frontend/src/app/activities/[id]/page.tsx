"use client";

import React, { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Footprints,
  Heart,
  Gauge,
  Flame,
  Mountain,
  Activity as ActivityIcon,
  Share2,
  Compass,
  CheckCircle,
  Copy,
  Zap,
  Clock,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { Activity, ActivitySample } from "@/lib/types";
import { formatDistance, formatDuration, formatPace, formatDate } from "@/lib/utils";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";

export default function ActivityDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const { data: activity, isLoading } = useSWR<Activity>(id ? `/activities/${id}` : null, fetchAPI);
  const { data: samples } = useSWR<ActivitySample[]>(id ? `/activities/${id}/samples` : null, fetchAPI);

  const [shareLink, setShareLink] = useState<string | null>(null);
  const [sharing, setSharing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [trailSaved, setTrailSaved] = useState(false);

  const handleShare = async () => {
    try {
      setSharing(true);
      const res = await fetchAPI<any>(`/share/activities/${id}`, {
        method: "POST",
        body: JSON.stringify({
          include_gps: true,
          include_hr: true,
          include_splits: true,
          expires_in_days: 30,
        }),
      });
      const fullUrl = `${window.location.origin}${res.share_url}`;
      setShareLink(fullUrl);
      await navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 4000);
    } catch (err) {
      console.error("Failed to create share link:", err);
    } finally {
      setSharing(false);
    }
  };

  const handleSaveAsTrail = async () => {
    try {
      await fetchAPI("/trails/from-activity", {
        method: "POST",
        body: JSON.stringify({
          activity_id: id,
          difficulty: "moderate",
          surface_type: "road",
        }),
      });
      setTrailSaved(true);
      setTimeout(() => setTrailSaved(false), 4000);
    } catch (err) {
      console.error("Failed to save as trail:", err);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-xs text-gray-500">Loading activity analysis...</div>;
  }

  if (!activity) {
    return (
      <div className="space-y-4">
        <Link href="/activities" className="text-xs text-cyan-400 flex items-center gap-1.5">
          <ArrowLeft className="h-4 w-4" /> Back to Activities
        </Link>
        <p className="text-gray-400">Activity record not found.</p>
      </div>
    );
  }

  // Samples format for dedicated charts
  const sampleData = samples || [];
  const hrPoints: DataPoint[] = sampleData.map((s, idx) => ({
    date: String(idx),
    value: s.heart_rate,
  }));

  const pacePoints: DataPoint[] = sampleData.map((s, idx) => ({
    date: String(idx),
    value: s.speed_ms && s.speed_ms > 0 ? Math.round((1000 / s.speed_ms / 60) * 100) / 100 : null,
  }));

  const elevPoints: DataPoint[] = sampleData.map((s, idx) => ({
    date: String(idx),
    value: s.altitude ? Math.round(s.altitude) : null,
  }));

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-2">
      {/* Header Back button */}
      <div>
        <Link
          href="/activities"
          className="text-xs text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1.5 mb-2 font-medium"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Explorer
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              {activity.name || "Workout Session"}
            </h1>
            <p className="text-xs text-gray-400 mt-1">
              {formatDate(activity.start_time)} • Garmin Activity #{activity.garmin_activity_id}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSaveAsTrail}
              className="px-3.5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-semibold text-white transition flex items-center gap-1.5"
            >
              {trailSaved ? (
                <>
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> Saved to Trails!
                </>
              ) : (
                <>
                  <Compass className="w-3.5 h-3.5 text-cyan-400" /> Convert to Trail
                </>
              )}
            </button>

            <button
              onClick={handleShare}
              disabled={sharing}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-bold text-xs tracking-wide shadow-lg shadow-cyan-500/20 transition flex items-center gap-1.5 disabled:opacity-50"
            >
              {copied ? (
                <>
                  <CheckCircle className="w-3.5 h-3.5" /> Link Copied to Clipboard!
                </>
              ) : (
                <>
                  <Share2 className="w-3.5 h-3.5" /> Share LiveTrack Link
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Share Link Banner if active */}
      {shareLink && (
        <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-xl p-3.5 flex items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2 truncate">
            <Share2 className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="text-gray-400">Public LiveTrack URL:</span>
            <span className="font-mono text-cyan-300 truncate">{shareLink}</span>
          </div>
          <button
            onClick={() => {
              navigator.clipboard.writeText(shareLink);
              setCopied(true);
              setTimeout(() => setCopied(false), 3000);
            }}
            className="px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-300 font-bold hover:bg-cyan-500/30 shrink-0 flex items-center gap-1"
          >
            <Copy className="w-3 h-3" /> {copied ? "Copied" : "Copy"}
          </button>
        </div>
      )}

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Distance</span>
          <div className="text-xl font-bold text-white mt-1">
            {formatDistance(activity.distance_meters)}
          </div>
        </div>
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Duration</span>
          <div className="text-xl font-bold text-white mt-1">
            {formatDuration(activity.duration_seconds)}
          </div>
        </div>
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Avg Pace</span>
          <div className="text-xl font-bold text-cyan-400 font-mono mt-1">
            {formatPace(activity.avg_speed_ms)}
          </div>
        </div>
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Avg HR</span>
          <div className="text-xl font-bold text-rose-400 font-mono mt-1">
            {activity.avg_heart_rate ? `${activity.avg_heart_rate} bpm` : "—"}
          </div>
        </div>
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Elevation</span>
          <div className="text-xl font-bold text-emerald-400 font-mono mt-1">
            {activity.elevation_gain != null ? `+${Math.round(activity.elevation_gain)} m` : "—"}
          </div>
        </div>
        <div className="bg-[#101726] border border-gray-800 rounded-xl p-4">
          <span className="text-[11px] text-gray-400 font-medium uppercase font-mono">Cadence</span>
          <div className="text-xl font-bold text-violet-400 font-mono mt-1">
            {activity.avg_cadence ? `${activity.avg_cadence} spm` : "—"}
          </div>
        </div>
      </div>

      {/* Dedicated Individual Telemetry Charts */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-white uppercase tracking-wider">
          Individual Telemetry Stream Charts
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricDetailChart
            title="Continuous Heart Rate Stream"
            description="Cardiovascular load progression across workout"
            currentValue={activity.avg_heart_rate}
            unit="bpm"
            data={hrPoints}
            type="line"
            color="rose"
            icon={Heart}
          />
          <MetricDetailChart
            title="Pace Progression"
            description="Speed and interval velocity splits"
            currentValue={formatPace(activity.avg_speed_ms)}
            unit=""
            data={pacePoints}
            type="line"
            color="emerald"
            icon={Clock}
          />
          <MetricDetailChart
            title="Course Elevation Profile"
            description="Altimeter barometric ascent & descent"
            currentValue={activity.elevation_gain ? `+${Math.round(activity.elevation_gain)}` : "—"}
            unit="m"
            data={elevPoints}
            type="area"
            color="cyan"
            icon={Mountain}
          />
        </div>
      </div>

      {/* Laps / Splits Table */}
      {activity.laps && activity.laps.length > 0 && (
        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Splits & Lap Breakdown
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-[10px] text-gray-400 border-b border-gray-800 font-mono uppercase">
                  <th className="pb-3 px-3 font-medium">Lap</th>
                  <th className="pb-3 px-3 font-medium">Distance</th>
                  <th className="pb-3 px-3 font-medium">Time</th>
                  <th className="pb-3 px-3 font-medium">Avg Pace</th>
                  <th className="pb-3 px-3 font-medium">Avg HR</th>
                  <th className="pb-3 px-3 font-medium">Cadence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50 font-mono">
                {activity.laps.map((l) => (
                  <tr key={l.lap_index} className="hover:bg-gray-900/40 transition">
                    <td className="py-2.5 px-3 font-bold text-white">Split {l.lap_index + 1}</td>
                    <td className="py-2.5 px-3 text-gray-300">
                      {formatDistance(l.distance_meters)}
                    </td>
                    <td className="py-2.5 px-3 text-gray-400">
                      {formatDuration(l.duration_seconds)}
                    </td>
                    <td className="py-2.5 px-3 text-cyan-400 font-mono text-xs">
                      {formatPace(l.avg_speed_ms)}
                    </td>
                    <td className="py-2.5 px-3 text-rose-400">
                      {l.avg_heart_rate ? `${l.avg_heart_rate} bpm` : "—"}
                    </td>
                    <td className="py-2.5 px-3 text-gray-400">
                      {l.avg_cadence ? `${l.avg_cadence} spm` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

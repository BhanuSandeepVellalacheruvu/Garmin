"use client";

import React, { useEffect, useState } from "react";
import {
  Radio,
  Play,
  Square,
  Share2,
  Heart,
  Timer,
  Navigation,
  Flame,
  Zap,
  Activity,
  CheckCircle,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface LiveSession {
  id: string;
  sport: string;
  status: string;
  start_time: string;
  elapsed_seconds: number;
  distance_meters: number;
  current_pace_sec: number | null;
  current_heart_rate: number | null;
  avg_heart_rate: number | null;
  max_heart_rate: number | null;
  current_cadence: number | null;
  elevation_gain_m: number;
  telemetry_count: number;
  telemetry_samples?: any[];
}

export default function LiveActivityPage() {
  const [session, setSession] = useState<LiveSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [sport, setSport] = useState("running");
  const [timerRunning, setTimerRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [telemetry, setTelemetry] = useState<any[]>([]);

  const checkActive = async () => {
    try {
      setLoading(true);
      const res = await fetchAPI<{ session: LiveSession | null }>("/live/active");
      if (res.session) {
        setSession(res.session);
        setElapsed(res.session.elapsed_seconds);
        // fetch full detail
        const det = await fetchAPI<any>(`/live/${res.session.id}`);
        setTelemetry(det.telemetry_samples || []);
      } else {
        setSession(null);
      }
    } catch (err) {
      console.error("Failed to check active live session:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkActive();
  }, []);

  // Timer tick for UI elapsed time
  useEffect(() => {
    let interval: any;
    if (session && session.status === "active") {
      interval = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [session]);

  const handleStart = async () => {
    try {
      const res = await fetchAPI<any>("/live/start", {
        method: "POST",
        body: JSON.stringify({ sport }),
      });
      await checkActive();
    } catch (err) {
      console.error("Failed to start session:", err);
    }
  };

  const handlePushSample = async () => {
    if (!session) return;
    try {
      const nextTime = elapsed + 5;
      const nextDist = session.distance_meters + 18.5; // ~18.5 meters in 5s (~4:30/km)
      const hr = Math.round(145 + Math.random() * 15);
      const cad = Math.round(168 + Math.random() * 6);
      const pace = 270; // 4:30 min/km

      await fetchAPI(`/live/${session.id}/telemetry`, {
        method: "POST",
        body: JSON.stringify({
          elapsed_seconds: nextTime,
          distance_meters: nextDist,
          current_pace_sec: pace,
          current_heart_rate: hr,
          current_cadence: cad,
          elevation_gain_m: session.elevation_gain_m + 0.5,
        }),
      });

      const newSample = {
        time: nextTime,
        hr: hr,
        pace: pace,
        cadence: cad,
      };
      setTelemetry((prev) => [...prev, newSample]);
      setSession((prev: any) => ({
        ...prev,
        elapsed_seconds: nextTime,
        distance_meters: nextDist,
        current_heart_rate: hr,
        current_cadence: cad,
      }));
    } catch (err) {
      console.error("Failed to push telemetry:", err);
    }
  };

  const handleStop = async () => {
    if (!session) return;
    try {
      await fetchAPI(`/live/${session.id}/stop`, { method: "POST" });
      alert("Workout completed and saved to your Garmin activities!");
      setSession(null);
      setTelemetry([]);
      setElapsed(0);
    } catch (err) {
      console.error("Failed to stop session:", err);
    }
  };

  const formatHMS = (sec: number) => {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.floor(sec % 60);
    return `${h > 0 ? `${h}:` : ""}${m.toString().padStart(2, "0")}:${s
      .toString()
      .padStart(2, "0")}`;
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Garmin Connect+ Live Experience
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Live Activity Track</h1>
          <p className="text-sm text-gray-400 mt-1">
            Real-time biometric telemetry, pace feedback, and LiveTrack course broadcasting.
          </p>
        </div>

        {session && (
          <div className="flex items-center gap-3">
            <button
              onClick={handlePushSample}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs text-white font-medium transition"
            >
              <Zap className="w-3.5 h-3.5 text-cyan-400" /> Push 5s Telemetry Sample
            </button>
            <button
              onClick={handleStop}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs tracking-wide transition shadow-lg shadow-rose-600/20"
            >
              <Square className="w-3.5 h-3.5" /> Stop & Save Activity
            </button>
          </div>
        )}
      </div>

      {!session ? (
        /* Start Session Card */
        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-8 max-w-xl mx-auto text-center space-y-6 shadow-xl">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto">
            <Radio className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white">Start New Live Activity</h2>
            <p className="text-xs text-gray-400">
              Select your sport type to initiate real-time telemetry streaming and LiveTrack
              broadcasting.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-left">
            {["running", "trail_running", "cycling", "treadmill"].map((s) => (
              <button
                key={s}
                onClick={() => setSport(s)}
                className={`p-3.5 rounded-xl border text-xs font-semibold capitalize transition ${
                  sport === s
                    ? "bg-cyan-500/10 border-cyan-500/40 text-cyan-300"
                    : "bg-gray-900 border-gray-800 text-gray-400 hover:border-gray-700"
                }`}
              >
                {s.replace("_", " ")}
              </button>
            ))}
          </div>

          <button
            onClick={handleStart}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-extrabold text-sm tracking-wide shadow-lg shadow-cyan-500/20 transition flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-black" /> Begin Live Workout
          </button>
        </div>
      ) : (
        /* Live Workout HUD */
        <div className="space-y-6">
          {/* Big Digital Display */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 text-center">
              <span className="text-[10px] font-mono uppercase text-gray-400 block mb-1">
                Elapsed Time
              </span>
              <span className="text-4xl md:text-5xl font-black text-white font-mono tracking-tight">
                {formatHMS(elapsed)}
              </span>
            </div>

            <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 text-center">
              <span className="text-[10px] font-mono uppercase text-gray-400 block mb-1">
                Distance
              </span>
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl md:text-5xl font-black text-cyan-400 font-mono tracking-tight">
                  {(session.distance_meters / 1000.0).toFixed(2)}
                </span>
                <span className="text-xs text-gray-400 font-bold">km</span>
              </div>
            </div>

            <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 text-center">
              <span className="text-[10px] font-mono uppercase text-gray-400 block mb-1">
                Current Heart Rate
              </span>
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl md:text-5xl font-black text-rose-500 font-mono tracking-tight">
                  {session.current_heart_rate ?? 148}
                </span>
                <span className="text-xs text-gray-400 font-bold">bpm</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 font-medium border border-rose-500/20 mt-2 inline-block">
                Zone 3 Tempo
              </span>
            </div>

            <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 text-center">
              <span className="text-[10px] font-mono uppercase text-gray-400 block mb-1">
                Pace & Cadence
              </span>
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl md:text-5xl font-black text-emerald-400 font-mono tracking-tight">
                  4:30
                </span>
                <span className="text-xs text-gray-400 font-bold">/km</span>
              </div>
              <span className="text-[10px] text-gray-400 font-mono mt-2 block">
                Cadence: {session.current_cadence ?? 172} spm
              </span>
            </div>
          </div>

          {/* Real-time Heart Rate Stream Chart */}
          <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Heart className="w-4 h-4 text-rose-500" /> Live Heart Rate Telemetry Stream
            </h3>
            <div className="h-64 w-full">
              {telemetry.length === 0 ? (
                <div className="h-full flex items-center justify-center text-xs text-gray-500">
                  Awaiting first telemetry packet. Click "Push 5s Telemetry Sample" above to stream.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={telemetry} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                    <XAxis dataKey="time" stroke="#4b5563" fontSize={10} unit="s" />
                    <YAxis domain={["dataMin - 5", "dataMax + 5"]} stroke="#4b5563" fontSize={10} unit=" bpm" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0B0F19",
                        borderColor: "#374151",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="hr"
                      stroke="#f43f5e"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: "#f43f5e" }}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

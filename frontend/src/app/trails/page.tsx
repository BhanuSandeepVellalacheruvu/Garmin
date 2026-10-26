"use client";

import React, { useEffect, useState } from "react";
import {
  Compass,
  Mountain,
  MapPin,
  Clock,
  Star,
  Plus,
  Trash2,
  Navigation,
  Activity as ActivityIcon,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";

interface Trail {
  id: string;
  name: string;
  description: string;
  activity_type: string;
  distance_km: number;
  elevation_gain_m: number;
  estimated_duration_s: number | null;
  difficulty: string;
  surface_type: string;
  is_favorite: boolean;
  created_at: string;
}

export default function TrailsPage() {
  const [trails, setTrails] = useState<Trail[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedActivityId, setSelectedActivityId] = useState("");
  const [creating, setCreating] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tRes, actRes] = await Promise.all([
        fetchAPI<Trail[]>("/trails"),
        fetchAPI<{ items: any[] }>("/activities?limit=15"),
      ]);
      setTrails(tRes || []);
      setActivities(actRes.items || []);
    } catch (err) {
      console.error("Failed to load trails:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateFromActivity = async () => {
    if (!selectedActivityId) return;
    try {
      setCreating(true);
      await fetchAPI("/trails/from-activity", {
        method: "POST",
        body: JSON.stringify({
          activity_id: selectedActivityId,
          difficulty: "moderate",
          surface_type: "road",
        }),
      });
      setSelectedActivityId("");
      await loadData();
    } catch (err) {
      console.error("Failed to create trail from activity:", err);
    } finally {
      setCreating(false);
    }
  };

  const handleToggleFavorite = async (id: string) => {
    try {
      await fetchAPI(`/trails/${id}/favorite`, { method: "POST" });
      setTrails(
        trails.map((t) => (t.id === id ? { ...t, is_favorite: !t.is_favorite } : t))
      );
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetchAPI(`/trails/${id}`, { method: "DELETE" });
      setTrails(trails.filter((t) => t.id !== id));
    } catch (err) {
      console.error("Failed to delete trail:", err);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5" /> Garmin Connect+ Route Explorer
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Garmin Trails & Courses</h1>
          <p className="text-sm text-gray-400 mt-1">
            Synthesize courses, analyze elevation gradients, and export GPX waypoints directly from
            historical runs.
          </p>
        </div>

        {/* Quick Route Synthesis from Activities */}
        <div className="flex items-center gap-2 bg-[#101726] border border-gray-800 p-2 rounded-xl">
          <select
            value={selectedActivityId}
            onChange={(e) => setSelectedActivityId(e.target.value)}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">Select past workout to convert...</option>
            {activities.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name || a.sport_type} ({(a.distance_meters / 1000).toFixed(1)} km)
              </option>
            ))}
          </select>
          <button
            onClick={handleCreateFromActivity}
            disabled={!selectedActivityId || creating}
            className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs transition disabled:opacity-50 flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" /> Save as Trail
          </button>
        </div>
      </div>

      {/* Trails Grid */}
      {loading ? (
        <div className="py-12 text-center text-gray-500 text-sm">Loading saved routes...</div>
      ) : trails.length === 0 ? (
        <div className="bg-[#101726] border border-gray-800 rounded-2xl p-12 text-center max-w-md mx-auto space-y-4">
          <div className="w-12 h-12 rounded-xl bg-gray-900 text-gray-500 flex items-center justify-center mx-auto">
            <Compass className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-white text-base">No Saved Trails Yet</h3>
          <p className="text-xs text-gray-400">
            Use the dropdown selector in the top right to instantly generate a Garmin trail route
            from your logged runs.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {trails.map((trail) => (
            <div
              key={trail.id}
              className="bg-[#101726] border border-gray-800 hover:border-gray-700 transition rounded-2xl p-5 flex flex-col justify-between space-y-4 shadow-sm"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="font-bold text-gray-100 text-base line-clamp-1">{trail.name}</h3>
                  <button
                    onClick={() => handleToggleFavorite(trail.id)}
                    className={`p-1 rounded transition ${
                      trail.is_favorite
                        ? "text-amber-400 fill-amber-400"
                        : "text-gray-600 hover:text-gray-400"
                    }`}
                  >
                    <Star className="w-4 h-4" />
                  </button>
                </div>

                <p className="text-xs text-gray-400 line-clamp-2 mb-4">
                  {trail.description || "Course profile synthesized from GPS trackpoints."}
                </p>

                {/* Stat pills */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-gray-900/60 p-2 rounded-lg border border-gray-800/60">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">Distance</span>
                    <span className="font-mono font-bold text-cyan-400 text-sm">
                      {trail.distance_km} km
                    </span>
                  </div>
                  <div className="bg-gray-900/60 p-2 rounded-lg border border-gray-800/60">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">Elevation Gain</span>
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      {trail.elevation_gain_m} m
                    </span>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-800/60 text-xs">
                <span className="capitalize px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 text-[10px] font-mono">
                  {trail.difficulty} • {trail.surface_type}
                </span>

                <button
                  onClick={() => handleDelete(trail.id)}
                  className="text-gray-600 hover:text-rose-400 p-1 transition"
                  title="Delete trail"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

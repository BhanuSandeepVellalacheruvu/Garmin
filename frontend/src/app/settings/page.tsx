"use client";

import { useState, useEffect } from "react";
import useSWR, { mutate } from "swr";
import { Settings as SettingsIcon, Key, Brain, User, ShieldCheck, Database, RefreshCw, Check } from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { GarminStatus } from "@/lib/types";

export default function SettingsPage() {
  const { data: status } = useSWR<GarminStatus>("/garmin/status", fetchAPI);
  const { data: profile } = useSWR<any>("/user/profile", fetchAPI);

  const [timezone, setTimezone] = useState("UTC");
  const [preferredUnits, setPreferredUnits] = useState("metric");
  const [experienceLevel, setExperienceLevel] = useState("intermediate");
  const [availabilityHours, setAvailabilityHours] = useState("6");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    if (profile) {
      if (profile.timezone) setTimezone(profile.timezone);
      if (profile.preferred_units) setPreferredUnits(profile.preferred_units);
      if (profile.experience_level) setExperienceLevel(profile.experience_level);
      if (profile.weekly_availability_hours) setAvailabilityHours(String(profile.weekly_availability_hours));
    }
  }, [profile]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchAPI("/user/profile", {
        method: "PATCH",
        body: JSON.stringify({
          timezone,
          preferred_units: preferredUnits,
          experience_level: experienceLevel,
          weekly_availability_hours: parseFloat(availabilityHours) || 6,
        }),
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
      mutate("/user/profile");
    } catch (err) {
      alert("Error saving settings");
    }
  };

  const handleFullSync = async () => {
    try {
      setIsSyncing(true);
      await fetchAPI("/garmin/sync/full", {
        method: "POST",
        body: JSON.stringify({}),
      });
      mutate("/garmin/status");
    } catch (err) {
      alert("Failed to initiate sync");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="h-6 w-6 text-cyan-400" />
          <span>Settings & Integrations</span>
        </h1>
        <p className="text-sm text-gray-400">
          Garmin Connect Personal API keys, open-weight LLM parameters, and personal athlete preferences.
        </p>
      </div>

      {/* Garmin Connect Integration Card */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Key className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Garmin Connect API</h2>
              <p className="text-xs text-gray-400">Official Personal API integration status</p>
            </div>
          </div>

          <span
            className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
              status?.is_demo_mode
                ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
            }`}
          >
            {status?.provider || "Loading..."}
          </span>
        </div>

        <div className="p-4 rounded-lg bg-gray-900/60 border border-gray-800 space-y-2 mb-6">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Capabilities Discovered:</span>
            <span className="text-gray-200 font-mono">
              {status?.capabilities?.join(", ") || "activities, sleep, hrv, stress"}
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Last Synced Records:</span>
            <span className="text-cyan-400 font-semibold">{status?.last_sync_records ?? 0}</span>
          </div>
        </div>

        {/* Instructions */}
        <div className="space-y-3 text-xs text-gray-300 border-t border-gray-800 pt-4">
          <h4 className="font-semibold text-white">How to connect your Garmin account:</h4>
          <ol className="list-decimal list-inside space-y-1 text-gray-400">
            <li>Log into Garmin Connect Web (connect.garmin.com)</li>
            <li>Navigate to Settings → Account Information → Personal API Keys</li>
            <li>Generate your Personal API Key</li>
            <li>
              Set <code className="text-cyan-300 font-mono">GARMIN_PROVIDER=official</code> and{" "}
              <code className="text-cyan-300 font-mono">GARMIN_PERSONAL_API_KEY=&lt;key&gt;</code> in your <code className="text-white font-mono">.env</code>
            </li>
          </ol>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={handleFullSync}
            disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isSyncing ? "animate-spin text-cyan-400" : ""}`} />
            <span>{isSyncing ? "Running Full Sync..." : "Trigger Full Historical Sync"}</span>
          </button>
        </div>
      </div>

      {/* LLM Engine Card */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-9 w-9 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-400 flex items-center justify-center">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Open-Weight AI Coach Engine</h2>
            <p className="text-xs text-gray-400">Local Ollama or OpenAI-compatible inference configuration</p>
          </div>
        </div>

        <div className="text-xs text-gray-400 space-y-2 mb-4">
          <p>
            The dashboard uses a local open-weight model (e.g. <span className="text-white font-mono">llama3.2</span> or <span className="text-white font-mono">mistral</span>) through Ollama, guaranteeing 100% data privacy and offline coaching.
          </p>
          <div className="p-3 bg-gray-900 rounded-lg border border-gray-800 font-mono text-[11px] text-gray-300 space-y-1">
            <p className="text-gray-500"># Start Ollama locally:</p>
            <p>ollama pull llama3.2</p>
            <p>ollama serve</p>
          </div>
        </div>
      </div>

      {/* Athlete Preferences Form */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-9 w-9 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
            <User className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Athlete Profile & Preferences</h2>
            <p className="text-xs text-gray-400">Customise metrics and training calculation inputs</p>
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Preferred Units</label>
              <select
                value={preferredUnits}
                onChange={(e) => setPreferredUnits(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="metric">Metric (km, min/km, meters)</option>
                <option value="imperial">Imperial (miles, min/mi, feet)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Timezone</label>
              <input
                type="text"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Experience Level</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="beginner">Beginner (&lt; 20 km/week)</option>
                <option value="intermediate">Intermediate (20–60 km/week)</option>
                <option value="advanced">Advanced (&gt; 60 km/week)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Weekly Training Availability (Hours)</label>
              <input
                type="number"
                step="0.5"
                value={availabilityHours}
                onChange={(e) => setAvailabilityHours(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-gray-800 flex items-center justify-between">
            {savedSuccess ? (
              <span className="text-xs text-emerald-400 flex items-center gap-1.5 font-medium">
                <Check className="h-4 w-4" /> Preferences updated successfully!
              </span>
            ) : (
              <span />
            )}
            <button
              type="submit"
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-gray-950 transition"
            >
              Save Preferences
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

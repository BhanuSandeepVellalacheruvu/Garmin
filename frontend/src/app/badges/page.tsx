"use client";

import React, { useEffect, useState } from "react";
import {
  Award,
  Trophy,
  Medal,
  CheckCircle,
  Lock,
  RotateCw,
  Sparkles,
  Flame,
  Moon,
  Sunrise,
  Mountain,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";

interface Badge {
  key: string;
  title: string;
  description: string;
  category: string;
  tier: "bronze" | "silver" | "gold" | "platinum";
  icon: string;
  is_unlocked: boolean;
  achieved_at: string | null;
  metric_value: number | null;
}

export default function BadgesPage() {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [unlockedCount, setUnlockedCount] = useState(0);
  const [completionPct, setCompletionPct] = useState(0);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [newlyUnlocked, setNewlyUnlocked] = useState<string[]>([]);

  const loadBadges = async () => {
    try {
      setLoading(true);
      const res = await fetchAPI<any>("/badges");
      setBadges(res.badges || []);
      setUnlockedCount(res.unlocked_count || 0);
      setCompletionPct(res.completion_pct || 0);
    } catch (err) {
      console.error("Failed to load badges:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBadges();
  }, []);

  const handleEvaluate = async () => {
    try {
      setEvaluating(true);
      const res = await fetchAPI<any>("/badges/evaluate", { method: "POST" });
      setNewlyUnlocked(res.newly_unlocked || []);
      await loadBadges();
    } catch (err) {
      console.error("Failed to evaluate badges:", err);
    } finally {
      setEvaluating(false);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "gold":
        return "from-amber-400 to-yellow-600 text-amber-300 border-amber-500/40";
      case "silver":
        return "from-slate-300 to-gray-400 text-slate-200 border-slate-400/40";
      default:
        return "from-amber-700 to-orange-900 text-amber-500 border-amber-700/40";
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-widest flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5" /> Garmin Connect+ Milestones
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Badges & Achievements
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Earn official badges by breaking personal distance records, consistency streaks, and
            recovery goals.
          </p>
        </div>

        <button
          onClick={handleEvaluate}
          disabled={evaluating}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-black font-bold text-xs tracking-wide shadow-lg shadow-amber-500/20 transition disabled:opacity-50"
        >
          {evaluating ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin" /> Scanning Activities...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" /> Evaluate My Achievements
            </>
          )}
        </button>
      </div>

      {/* Newly Unlocked Alert if any */}
      {newlyUnlocked.length > 0 && (
        <div className="bg-gradient-to-r from-amber-950/40 via-yellow-950/30 to-orange-950/40 border border-amber-500/30 rounded-2xl p-4 flex items-center gap-3">
          <Trophy className="w-6 h-6 text-amber-400 shrink-0" />
          <div className="text-xs">
            <span className="font-bold text-amber-300 block">Newly Unlocked Badges!</span>
            <span className="text-gray-300">
              Congratulations! You unlocked: {newlyUnlocked.join(", ")}
            </span>
          </div>
        </div>
      )}

      {/* Progress Banner */}
      <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-mono uppercase text-gray-400">Total Unlocked Progress</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-4xl font-extrabold text-white font-mono">{unlockedCount}</span>
            <span className="text-gray-400 text-sm">/ {badges.length} Badges</span>
          </div>
        </div>

        <div className="w-full md:w-80 space-y-2">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-gray-400">Completion</span>
            <span className="text-amber-400 font-mono font-bold">{completionPct}%</span>
          </div>
          <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full transition-all duration-500"
              style={{ width: `${completionPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Badges Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {loading ? (
          <div className="col-span-full py-12 text-center text-gray-500 text-sm">
            Loading achievement badges...
          </div>
        ) : (
          badges.map((b) => (
            <div
              key={b.key}
              className={`rounded-2xl border p-4 flex flex-col items-center text-center justify-between space-y-3 transition ${
                b.is_unlocked
                  ? "bg-[#101726] border-amber-500/30 hover:border-amber-500/50 shadow-md shadow-amber-500/5"
                  : "bg-gray-900/30 border-gray-800/80 opacity-60"
              }`}
            >
              {/* Badge Icon Medal */}
              <div
                className={`w-14 h-14 rounded-2xl flex items-center justify-center border bg-gradient-to-br shadow-inner ${
                  b.is_unlocked
                    ? getTierColor(b.tier)
                    : "from-gray-800 to-gray-900 text-gray-600 border-gray-800"
                }`}
              >
                {b.is_unlocked ? (
                  <Trophy className="w-7 h-7" />
                ) : (
                  <Lock className="w-6 h-6 text-gray-600" />
                )}
              </div>

              <div>
                <h3 className="font-bold text-white text-xs mb-1">{b.title}</h3>
                <p className="text-[11px] text-gray-400 leading-tight line-clamp-3">
                  {b.description}
                </p>
              </div>

              <div className="pt-2 border-t border-gray-800/60 w-full text-[10px] font-mono">
                {b.is_unlocked ? (
                  <span className="text-emerald-400 font-semibold flex items-center justify-center gap-1">
                    <CheckCircle className="w-3 h-3" /> Unlocked
                  </span>
                ) : (
                  <span className="text-gray-500">Locked</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

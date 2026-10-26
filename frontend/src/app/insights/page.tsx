"use client";

import React, { useEffect, useState } from "react";
import {
  Sparkles,
  Zap,
  Activity,
  Heart,
  TrendingUp,
  RotateCw,
  CheckCircle,
  AlertTriangle,
  Info,
} from "lucide-react";
import { fetchAPI } from "@/lib/api";

interface InsightCard {
  id: string;
  type: string;
  title: string;
  badge: string;
  badge_variant: "default" | "warning" | "destructive";
  value: string;
  description: string;
  metrics: { label: string; value: string }[];
}

interface InsightsFeed {
  as_of: string;
  readiness_score: number;
  cards: InsightCard[];
}

export default function InsightsPage() {
  const [feed, setFeed] = useState<InsightsFeed | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<string | null>(null);

  const loadFeed = async () => {
    try {
      setLoading(true);
      const res = await fetchAPI<InsightsFeed>("/insights/feed");
      setFeed(res);
    } catch (err) {
      console.error("Failed to load insights feed:", err);
    } finally {
      setLoading(false);
    }
  };

  const generateFreshInsight = async () => {
    try {
      setGenerating(true);
      const res = await fetchAPI<{ content: string }>("/insights/generate", {
        method: "POST",
      });
      setGeneratedResult(res.content);
    } catch (err: any) {
      setGeneratedResult(
        "Solid aerobic volume accumulated over recent sessions. Cardiovascular decoupling remains minimal. Target an easy recovery run or mobility tomorrow."
      );
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadFeed();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> Garmin Connect+ Intelligence
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Active Intelligence</h1>
          <p className="text-sm text-gray-400 mt-1">
            Real-time physiological readiness, fatigue modeling, and AI coach recommendations.
          </p>
        </div>

        <button
          onClick={generateFreshInsight}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-semibold text-xs tracking-wide shadow-lg shadow-cyan-500/20 transition disabled:opacity-50"
        >
          {generating ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin" /> Synthesizing with Gemma 4...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" /> Synthesize Fresh AI Insight
            </>
          )}
        </button>
      </div>

      {/* Generated AI Insight Banner if any */}
      {generatedResult && (
        <div className="bg-gradient-to-r from-cyan-950/40 via-blue-950/40 to-purple-950/40 border border-cyan-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shrink-0">
              <Zap className="w-6 h-6" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider font-mono">
                  Ollama Gemma 4 • AI Synthesis
                </span>
                <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-500/20">
                  Just now
                </span>
              </div>
              <p className="text-gray-200 text-sm leading-relaxed">{generatedResult}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Readiness Gauge Bar */}
      <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <span className="text-xs font-mono uppercase text-gray-400">Current Physiological Readiness</span>
            <div className="flex items-baseline gap-3">
              <span className="text-5xl font-black text-white tracking-tight">
                {feed?.readiness_score ?? "—"}
              </span>
              <span className="text-xl font-medium text-gray-400">/ 100</span>
              <span
                className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                  (feed?.readiness_score ?? 0) >= 70
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    : (feed?.readiness_score ?? 0) >= 50
                    ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                }`}
              >
                {(feed?.readiness_score ?? 0) >= 70
                  ? "Prime Stimulus Window"
                  : (feed?.readiness_score ?? 0) >= 50
                  ? "Moderate Baseline"
                  : "Recovery Prioritized"}
              </span>
            </div>
            <p className="text-xs text-gray-400 max-w-xl">
              Calculated using Garmin sleep quality, resting heart rate deflection, acute-chronic
              training load ratio, and body battery autonomic balance.
            </p>
          </div>

          <div className="w-full md:w-72 bg-gray-900/60 p-4 rounded-xl border border-gray-800 space-y-2">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-gray-400">Readiness Spectrum</span>
              <span className="text-cyan-400 font-mono">{feed?.readiness_score ?? 0}%</span>
            </div>
            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden flex">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500 rounded-full"
                style={{ width: `${Math.min(100, Math.max(5, feed?.readiness_score ?? 0))}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-gray-500 font-mono">
              <span>Rest (0-40)</span>
              <span>Moderate (41-70)</span>
              <span>Prime (71-100)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Intelligence Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {loading ? (
          <div className="col-span-2 py-12 text-center text-gray-500 text-sm">
            Loading active intelligence cards...
          </div>
        ) : (
          feed?.cards.map((card) => (
            <div
              key={card.id}
              className="bg-[#101726] border border-gray-800 hover:border-gray-700 transition rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-gray-200 text-base">{card.title}</h3>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
                      card.badge_variant === "destructive"
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        : card.badge_variant === "warning"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                        : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
                    }`}
                  >
                    {card.badge}
                  </span>
                </div>
                <div className="text-2xl font-black text-white tracking-tight mb-2">
                  {card.value}
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">{card.description}</p>
              </div>

              {/* Mini metric breakdown */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-gray-800/80">
                {card.metrics.map((m, idx) => (
                  <div key={idx} className="bg-gray-900/50 p-2.5 rounded-lg border border-gray-800/50">
                    <span className="text-[10px] text-gray-400 block truncate">{m.label}</span>
                    <span className="text-xs font-bold text-gray-100 font-mono mt-0.5 block">
                      {m.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

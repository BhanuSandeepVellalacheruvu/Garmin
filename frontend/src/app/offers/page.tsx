"use client";

import React, { useEffect, useState } from "react";
import { Flame, CheckCircle, Gift, Sparkles, ExternalLink, ShieldCheck } from "lucide-react";
import { fetchAPI } from "@/lib/api";

export default function OffersPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetchAPI<any>("/offers");
        setData(res);
      } catch (err) {
        console.error("Failed to load offers:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-bold text-amber-400 uppercase tracking-widest flex items-center gap-1.5">
            <Flame className="w-3.5 h-3.5" /> Garmin Connect+ Member Privileges
          </span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Connect+ & Partner Perks</h1>
        <p className="text-sm text-gray-400 mt-1">
          Your active Connect+ features, private AI intelligence tier, and exclusive athlete discounts.
        </p>
      </div>

      {/* Subscription Status Banner */}
      <div className="bg-gradient-to-r from-cyan-950/40 via-blue-950/40 to-indigo-950/40 border border-cyan-500/30 rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">Tier: {data?.tier || "Connect+ Pro"}</h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold uppercase border border-emerald-500/30">
                Active
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Full unconstrained access to high-frequency telemetry, AI active intelligence, and private
              Ollama Cloud inference.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 font-mono">Status: Connected to Garmin Connect</span>
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>

      {/* Active Features Included */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider">
          Included Connect+ Intelligence Modules
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data?.features || []).map((feat: any) => (
            <div
              key={feat.id}
              className="bg-[#101726] border border-gray-800 rounded-2xl p-5 flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-white text-sm">{feat.title}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {feat.badge}
                  </span>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">{feat.description}</p>
              </div>

              <div className="flex items-center gap-1.5 text-xs text-emerald-400 pt-3 border-t border-gray-800/60 font-medium">
                <CheckCircle className="w-3.5 h-3.5" /> Enabled & Integrated
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Partner Perks */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider">
          Partner Athlete Benefits
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(data?.partner_perks || []).map((perk: any, idx: number) => (
            <div
              key={idx}
              className="bg-[#101726] border border-gray-800 rounded-2xl p-5 flex flex-col justify-between space-y-3"
            >
              <div>
                <span className="text-[10px] font-mono uppercase text-gray-500 block mb-1">
                  {perk.partner}
                </span>
                <h4 className="font-bold text-white text-sm mb-1">{perk.offer}</h4>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-gray-800/60 text-xs">
                <span className="font-mono bg-gray-900 border border-gray-800 px-2.5 py-1 rounded text-cyan-400 font-bold">
                  {perk.code}
                </span>
                <span className="text-gray-400 text-[11px]">{perk.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

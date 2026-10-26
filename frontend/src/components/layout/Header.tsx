"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { RefreshCw, CheckCircle2, AlertCircle, Database } from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { GarminStatus } from "@/lib/types";

export function Header() {
  const [syncing, setSyncing] = useState(false);
  const { data: status } = useSWR<GarminStatus>("/garmin/status", fetchAPI, {
    refreshInterval: 15000,
  });

  const handleManualSync = async () => {
    try {
      setSyncing(true);
      await fetchAPI("/garmin/sync", { method: "POST" });
      mutate("/garmin/status");
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setSyncing(false), 1200);
    }
  };

  return (
    <header className="h-16 border-b border-gray-800 bg-[#070B14]/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-gray-200">Garmin Connect Integration</h2>
        {status?.is_demo_mode && (
          <span className="text-[11px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Demo Mode Active
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        {status?.last_sync && (
          <span className="text-xs text-gray-400 flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            Last Synced: {new Date(status.last_sync).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        )}

        <button
          onClick={handleManualSync}
          disabled={syncing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800/80 hover:bg-gray-700/80 text-gray-200 border border-gray-700 transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${syncing ? "animate-spin text-cyan-400" : ""}`} />
          <span>{syncing ? "Syncing..." : "Sync Garmin"}</span>
        </button>
      </div>
    </header>
  );
}

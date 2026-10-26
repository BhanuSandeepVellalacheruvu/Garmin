"use client";

import { useState } from "react";
import useSWR from "swr";
import { Sparkles, X } from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { GarminStatus } from "@/lib/types";

export function DemoModeBanner() {
  const [dismissed, setDismissed] = useState(false);
  const { data: status } = useSWR<GarminStatus>("/garmin/status", fetchAPI);

  if (dismissed || !status?.is_demo_mode) return null;

  return (
    <div className="bg-gradient-to-r from-cyan-950/80 via-blue-950/70 to-slate-900/90 border-b border-cyan-800/40 px-6 py-2.5 flex items-center justify-between text-xs text-cyan-200">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-cyan-400 shrink-0" />
        <span>
          <strong className="text-white font-medium">Demo Mode:</strong> Displaying deterministic synthetic training data. Connect your Garmin Connect Personal API key in Settings to sync your real workouts.
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="p-1 text-cyan-400 hover:text-white transition rounded"
        title="Dismiss for session"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

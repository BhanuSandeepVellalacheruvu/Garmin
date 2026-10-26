import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number | null | undefined;
  unit?: string;
  icon: LucideIcon;
  subtext?: string;
  trend?: "up" | "down" | "neutral";
  trendLabel?: string;
  accentColor?: "cyan" | "emerald" | "violet" | "amber" | "rose";
}

export function MetricCard({
  title,
  value,
  unit,
  icon: Icon,
  subtext,
  trend,
  trendLabel,
  accentColor = "cyan",
}: MetricCardProps) {
  const colorMap = {
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    violet: "text-violet-400 bg-violet-500/10 border-violet-500/20",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  };

  return (
    <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-5 hover:border-gray-700/80 transition shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-gray-400 tracking-wide uppercase">{title}</span>
        <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center border", colorMap[accentColor])}>
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-bold tracking-tight text-white">
          {value != null && value !== "" ? value : "—"}
        </span>
        {unit && <span className="text-xs font-medium text-gray-400">{unit}</span>}
      </div>

      {(subtext || trendLabel) && (
        <div className="mt-2.5 flex items-center justify-between text-xs text-gray-400">
          <span>{subtext}</span>
          {trendLabel && (
            <span
              className={cn(
                "text-[11px] font-medium px-1.5 py-0.5 rounded",
                trend === "up" && "text-emerald-400 bg-emerald-500/10",
                trend === "down" && "text-rose-400 bg-rose-500/10",
                trend === "neutral" && "text-gray-400 bg-gray-800"
              )}
            >
              {trendLabel}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

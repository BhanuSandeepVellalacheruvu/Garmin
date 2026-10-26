"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Activity, LucideIcon, Info, AlertCircle, CheckCircle2, Calculator } from "lucide-react";

export interface DataPoint {
  date: string;
  value: number | null | undefined;
  [key: string]: any;
}

export interface MetricProvenance {
  source: string; // "Garmin API" | "Calculated" | "Unavailable"
  status?: "verified" | "calculated" | "unavailable";
  reason?: string;
  unit?: string;
}

interface MetricDetailChartProps {
  title: string;
  description?: string;
  currentValue?: string | number | null;
  unit?: string;
  data: DataPoint[];
  dataKey?: string;
  type?: "area" | "line" | "bar";
  color?: string; // hex or tailwind name
  height?: number;
  yAxisDomain?: [number | "auto" | "dataMin", number | "auto" | "dataMax"];
  icon?: LucideIcon;
  badge?: string;
  badgeVariant?: "default" | "success" | "warning" | "destructive" | "unavailable";
  provenance?: MetricProvenance;
  isUnavailable?: boolean;
  unavailableReason?: string;
  isPace?: boolean;
  formatValue?: (val: any) => string;
}

const COLOR_MAP: Record<string, { stroke: string; fill: string }> = {
  cyan: { stroke: "#06b6d4", fill: "#06b6d4" },
  emerald: { stroke: "#10b981", fill: "#10b981" },
  blue: { stroke: "#3b82f6", fill: "#3b82f6" },
  amber: { stroke: "#f59e0b", fill: "#f59e0b" },
  rose: { stroke: "#f43f5e", fill: "#f43f5e" },
  violet: { stroke: "#8b5cf6", fill: "#8b5cf6" },
  orange: { stroke: "#f97316", fill: "#f97316" },
};

export function MetricDetailChart({
  title,
  description,
  currentValue,
  unit = "",
  data = [],
  dataKey = "value",
  type = "area",
  color = "cyan",
  height = 190,
  yAxisDomain = ["auto", "auto"],
  icon: Icon = Activity,
  badge,
  badgeVariant,
  provenance,
  isUnavailable = false,
  unavailableReason,
  isPace = false,
  formatValue,
}: MetricDetailChartProps) {
  const colorConfig = COLOR_MAP[color] || { stroke: color, fill: color };

  const effectiveUnavailable = isUnavailable || provenance?.status === "unavailable";
  const effectiveReason =
    unavailableReason || provenance?.reason || "Metric unavailable from current sensor setup";

  const validData = data.filter((d) => d[dataKey] !== null && d[dataKey] !== undefined);
  const hasData = validData.length > 0 && !effectiveUnavailable;

  // Format date helper for X-axis
  const formatXAxis = (tick: string) => {
    if (!tick) return "";
    if (tick.includes("-")) {
      const parts = tick.split("-");
      if (parts.length >= 3) {
        return `${parts[1]}/${parts[2]}`;
      }
      if (parts.length === 2) {
        return tick;
      }
    }
    return tick;
  };

  // Format seconds to mm:ss for pace
  const formatSecondsToPace = (sec: number) => {
    if (!sec || isNaN(sec)) return "—";
    const mins = Math.floor(sec / 60);
    const remainder = Math.round(sec % 60);
    return `${mins}:${remainder.toString().padStart(2, "0")}`;
  };

  const formatTooltipValue = (val: any) => {
    if (formatValue) return formatValue(val);
    if (isPace && typeof val === "number") {
      return `${formatSecondsToPace(val)} /km`;
    }
    return `${val} ${unit}`.trim();
  };

  const formatYAxisTick = (val: any) => {
    if (isPace && typeof val === "number") {
      return formatSecondsToPace(val);
    }
    return val;
  };

  // Determine provenance badge details
  const renderProvenanceBadge = () => {
    if (provenance) {
      if (provenance.status === "unavailable") {
        return (
          <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium bg-gray-800/80 text-gray-400 border-gray-700 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 text-gray-400" />
            Unavailable
          </span>
        );
      }
      if (provenance.status === "calculated") {
        return (
          <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium bg-amber-500/10 text-amber-400 border-amber-500/20 flex items-center gap-1">
            <Calculator className="w-3 h-3 text-amber-400" />
            {provenance.source}
          </span>
        );
      }
      return (
        <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium bg-cyan-500/10 text-cyan-400 border-cyan-500/20 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3 text-cyan-400" />
          {provenance.source}
        </span>
      );
    }

    if (badge) {
      const variantClass =
        badgeVariant === "success"
          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
          : badgeVariant === "warning"
          ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
          : badgeVariant === "destructive"
          ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
          : badgeVariant === "unavailable"
          ? "bg-gray-800 text-gray-400 border-gray-700"
          : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";

      return (
        <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${variantClass}`}>
          {badge}
        </span>
      );
    }

    return null;
  };

  return (
    <div className="bg-[#101726] border border-gray-800 rounded-xl p-4 flex flex-col justify-between hover:border-gray-700 transition shadow-sm">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-2">
            <div
              className="p-1.5 rounded-lg border flex items-center justify-center"
              style={{
                backgroundColor: `${colorConfig.stroke}15`,
                borderColor: `${colorConfig.stroke}30`,
                color: colorConfig.stroke,
              }}
            >
              <Icon className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-gray-200">{title}</h3>
          </div>
          {renderProvenanceBadge()}
        </div>

        {description && (
          <p className="text-xs text-gray-400 line-clamp-1 mb-2">{description}</p>
        )}

        <div className="flex items-baseline gap-1.5 mt-2 mb-3">
          {effectiveUnavailable ? (
            <span className="text-xl font-bold tracking-tight text-gray-400">Unavailable</span>
          ) : (
            <>
              <span className="text-2xl font-bold tracking-tight text-white">
                {currentValue !== undefined && currentValue !== null ? currentValue : "—"}
              </span>
              {unit && <span className="text-xs text-gray-400 font-medium">{unit}</span>}
            </>
          )}
        </div>
      </div>

      {/* Chart visualization */}
      <div className="w-full relative mt-1" style={{ height }}>
        {effectiveUnavailable ? (
          <div className="w-full h-full flex flex-col items-center justify-center border border-dashed border-gray-800 rounded-lg p-3 text-center bg-gray-900/40">
            <div className="w-8 h-8 rounded-full bg-gray-800/80 flex items-center justify-center text-gray-400 mb-2">
              <Info className="w-4 h-4" />
            </div>
            <p className="text-xs font-medium text-gray-300">Requires External Sensor</p>
            <p className="text-[11px] text-gray-400 mt-1 max-w-[240px] leading-snug">
              {effectiveReason}
            </p>
          </div>
        ) : !hasData ? (
          <div className="w-full h-full flex flex-col items-center justify-center border border-dashed border-gray-800/80 rounded-lg text-gray-400 text-xs gap-1 bg-gray-900/30">
            <span>No activity data recorded in period</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {type === "area" ? (
              <AreaChart data={data} margin={{ top: 8, right: 6, left: isPace ? -10 : -24, bottom: 0 }}>
                <defs>
                  <linearGradient id={`grad-${title.replace(/\s+/g, "-")}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={colorConfig.stroke} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={colorConfig.stroke} stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatXAxis}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={yAxisDomain}
                  reversed={isPace}
                  tickFormatter={formatYAxisTick}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0B0F19",
                    borderColor: "#374151",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#f3f4f6",
                  }}
                  formatter={(val: any) => [formatTooltipValue(val), title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Area
                  type="monotone"
                  dataKey={dataKey}
                  stroke={colorConfig.stroke}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill={`url(#grad-${title.replace(/\s+/g, "-")})`}
                />
              </AreaChart>
            ) : type === "bar" ? (
              <BarChart data={data} margin={{ top: 8, right: 6, left: isPace ? -10 : -24, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatXAxis}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={yAxisDomain}
                  reversed={isPace}
                  tickFormatter={formatYAxisTick}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0B0F19",
                    borderColor: "#374151",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#f3f4f6",
                  }}
                  formatter={(val: any) => [formatTooltipValue(val), title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Bar dataKey={dataKey} fill={colorConfig.stroke} radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <LineChart data={data} margin={{ top: 8, right: 6, left: isPace ? -10 : -24, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatXAxis}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={yAxisDomain}
                  reversed={isPace}
                  tickFormatter={formatYAxisTick}
                  stroke="#4b5563"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0B0F19",
                    borderColor: "#374151",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#f3f4f6",
                  }}
                  formatter={(val: any) => [formatTooltipValue(val), title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Line
                  type="monotone"
                  dataKey={dataKey}
                  stroke={colorConfig.stroke}
                  strokeWidth={2}
                  dot={{ r: 3, fill: colorConfig.stroke }}
                  connectNulls={true}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

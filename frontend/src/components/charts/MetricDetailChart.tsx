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
import { Activity, LucideIcon } from "lucide-react";

export interface DataPoint {
  date: string;
  value: number | null | undefined;
  [key: string]: any;
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
  badgeVariant?: "default" | "success" | "warning" | "destructive";
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
  badgeVariant = "default",
}: MetricDetailChartProps) {
  const colorConfig = COLOR_MAP[color] || { stroke: color, fill: color };

  const validData = data.filter((d) => d[dataKey] !== null && d[dataKey] !== undefined);
  const hasData = validData.length > 0;

  // Format date helper
  const formatXAxis = (tick: string) => {
    if (!tick) return "";
    if (tick.includes("-")) {
      const parts = tick.split("-");
      if (parts.length >= 3) {
        return `${parts[1]}/${parts[2]}`;
      }
    }
    return tick;
  };

  const getBadgeClasses = (variant: string) => {
    switch (variant) {
      case "success":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "warning":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "destructive":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
    }
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
          {badge && (
            <span
              className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${getBadgeClasses(
                badgeVariant
              )}`}
            >
              {badge}
            </span>
          )}
        </div>

        {description && (
          <p className="text-xs text-gray-400 line-clamp-1 mb-2">{description}</p>
        )}

        <div className="flex items-baseline gap-1.5 mt-2 mb-3">
          <span className="text-2xl font-bold tracking-tight text-white">
            {currentValue !== undefined && currentValue !== null ? currentValue : "—"}
          </span>
          {unit && <span className="text-xs text-gray-400 font-medium">{unit}</span>}
        </div>
      </div>

      {/* Chart visualization */}
      <div className="w-full relative mt-1" style={{ height }}>
        {!hasData ? (
          <div className="w-full h-full flex flex-col items-center justify-center border border-dashed border-gray-800/80 rounded-lg text-gray-500 text-xs gap-1 bg-gray-900/30">
            <span>No data recorded for this metric</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {type === "area" ? (
              <AreaChart data={data} margin={{ top: 8, right: 6, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
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
                  formatter={(val: any) => [`${val} ${unit}`, title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Area
                  type="monotone"
                  dataKey={dataKey}
                  stroke={colorConfig.stroke}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill={`url(#grad-${title})`}
                />
              </AreaChart>
            ) : type === "bar" ? (
              <BarChart data={data} margin={{ top: 8, right: 6, left: -24, bottom: 0 }}>
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
                  formatter={(val: any) => [`${val} ${unit}`, title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Bar dataKey={dataKey} fill={colorConfig.stroke} radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <LineChart data={data} margin={{ top: 8, right: 6, left: -24, bottom: 0 }}>
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
                  formatter={(val: any) => [`${val} ${unit}`, title]}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Line
                  type="monotone"
                  dataKey={dataKey}
                  stroke={colorConfig.stroke}
                  strokeWidth={2}
                  dot={{ r: 2, fill: colorConfig.stroke }}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

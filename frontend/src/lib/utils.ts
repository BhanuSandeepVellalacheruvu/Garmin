import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDistance(meters: number | null | undefined, unit: "km" | "mi" = "km"): string {
  if (meters == null) return "—";
  if (unit === "mi") {
    return `${(meters / 1609.344).toFixed(2)} mi`;
  }
  return `${(meters / 1000).toFixed(2)} km`;
}

export function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null) return "—";
  const sec = Math.round(seconds);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  if (h > 0) {
    return `${h}h ${m}m ${s}s`;
  }
  return `${m}m ${s}s`;
}

export function formatPace(speedMs: number | null | undefined, unit: "km" | "mi" = "km"): string {
  if (!speedMs || speedMs <= 0) return "—";
  const factor = unit === "km" ? 1000 : 1609.344;
  const secPerUnit = factor / speedMs;
  const m = Math.floor(secPerUnit / 60);
  const s = Math.round(secPerUnit % 60);
  return `${m}:${s < 10 ? "0" : ""}${s} /${unit}`;
}

export function formatDate(isoStr: string | null | undefined): string {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return isoStr;
  }
}

export function getSportEmoji(sport: string | null | undefined): string {
  if (!sport) return "🏃";
  const s = sport.toLowerCase();
  if (s.includes("run")) return "🏃";
  if (s.includes("cycl") || s.includes("bike")) return "🚴";
  if (s.includes("swim")) return "🏊";
  if (s.includes("walk") || s.includes("hike")) return "🥾";
  if (s.includes("strength") || s.includes("weight")) return "🏋️";
  return "⚡";
}

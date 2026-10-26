"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { Search, Download, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { Activity } from "@/lib/types";
import { formatDistance, formatDuration, formatPace, formatDate, getSportEmoji } from "@/lib/utils";

export default function ActivitiesPage() {
  const [sportFilter, setSportFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 15;

  const queryParams = new URLSearchParams({
    limit: String(pageSize),
    offset: String(page * pageSize),
  });
  if (sportFilter) queryParams.set("sport_type", sportFilter);

  const { data, isLoading } = useSWR<{ items: Activity[]; total: number }>(
    `/activities?${queryParams.toString()}`,
    fetchAPI
  );

  const activities = (data?.items || []).filter((a) => {
    if (!searchQuery) return true;
    return a.name?.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const totalPages = Math.ceil((data?.total || 0) / pageSize);

  const handleExportCSV = () => {
    window.open(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/activities/export/csv`, "_blank");
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Activity Explorer</h1>
          <p className="text-sm text-gray-400">
            Search, filter, analyze splits, and export historical Garmin workouts.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition"
        >
          <Download className="h-4 w-4" />
          <span>Export to CSV</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <Search className="h-4 w-4 text-gray-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search workouts by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white focus:outline-none focus:border-cyan-400"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={sportFilter}
            onChange={(e) => {
              setSportFilter(e.target.value);
              setPage(0);
            }}
            className="px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-xs text-gray-300 focus:outline-none focus:border-cyan-400"
          >
            <option value="">All Sports</option>
            <option value="running">Running</option>
            <option value="cycling">Cycling</option>
            <option value="strength_training">Strength Training</option>
            <option value="swimming">Swimming</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-[11px] text-gray-400 border-b border-gray-800/80 bg-gray-900/40">
                <th className="py-3.5 px-4 font-medium">Activity</th>
                <th className="py-3.5 px-4 font-medium">Date</th>
                <th className="py-3.5 px-4 font-medium">Distance</th>
                <th className="py-3.5 px-4 font-medium">Duration</th>
                <th className="py-3.5 px-4 font-medium">Pace</th>
                <th className="py-3.5 px-4 font-medium">Avg HR</th>
                <th className="py-3.5 px-4 font-medium">Elevation</th>
                <th className="py-3.5 px-4 font-medium">Calories</th>
                <th className="py-3.5 px-4 font-medium text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-xs text-gray-500">
                    Loading activities...
                  </td>
                </tr>
              ) : activities.length > 0 ? (
                activities.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-800/30 transition">
                    <td className="py-3.5 px-4 font-medium text-white flex items-center gap-2">
                      <span>{getSportEmoji(a.sport_type)}</span>
                      <span className="truncate max-w-[200px]">{a.name || "Workout"}</span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-400">{formatDate(a.start_time)}</td>
                    <td className="py-3.5 px-4 text-gray-200 font-semibold">{formatDistance(a.distance_meters)}</td>
                    <td className="py-3.5 px-4 text-gray-400">{formatDuration(a.duration_seconds)}</td>
                    <td className="py-3.5 px-4 text-cyan-400 font-mono text-xs">{formatPace(a.avg_speed_ms)}</td>
                    <td className="py-3.5 px-4 text-gray-400">{a.avg_heart_rate ? `${a.avg_heart_rate} bpm` : "—"}</td>
                    <td className="py-3.5 px-4 text-gray-400">
                      {a.elevation_gain != null ? `+${Math.round(a.elevation_gain)} m` : "—"}
                    </td>
                    <td className="py-3.5 px-4 text-gray-400">{a.calories ? `${a.calories} kcal` : "—"}</td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/activities/${a.id}`}
                        className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
                      >
                        Inspect →
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-xs text-gray-500">
                    No matching activities found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
            <span>
              Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, data?.total || 0)} of {data?.total || 0}
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded border border-gray-800 hover:bg-gray-800 disabled:opacity-40 transition"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="font-semibold text-gray-200">
                {page + 1} / {totalPages}
              </span>
              <button
                disabled={page + 1 >= totalPages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded border border-gray-800 hover:bg-gray-800 disabled:opacity-40 transition"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

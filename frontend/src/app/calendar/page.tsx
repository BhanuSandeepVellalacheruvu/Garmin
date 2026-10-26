"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { Calendar as CalendarIcon, Plus, Flag, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { fetchAPI } from "@/lib/api";
import { CalendarEvent } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export default function CalendarPage() {
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth() + 1);

  const [goalModalOpen, setGoalModalOpen] = useState(false);
  const [raceName, setRaceName] = useState("");
  const [raceDate, setRaceDate] = useState("");
  const [distanceKm, setDistanceKm] = useState("21.1");
  const [targetTimeStr, setTargetTimeStr] = useState("1:45:00");

  const { data: calendar } = useSWR<CalendarEvent>(
    `/training/calendar?year=${currentYear}&month=${currentMonth}`,
    fetchAPI
  );

  const prevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const nextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const parts = targetTimeStr.split(":").map(Number);
      let totalSeconds = 0;
      if (parts.length === 3) totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
      else if (parts.length === 2) totalSeconds = parts[0] * 60 + parts[1];

      await fetchAPI("/training/goals", {
        method: "POST",
        body: JSON.stringify({
          race_name: raceName,
          race_date: raceDate || null,
          distance_meters: parseFloat(distanceKm) * 1000,
          target_time_seconds: totalSeconds || null,
        }),
      });

      setGoalModalOpen(false);
      setRaceName("");
      mutate(`/training/calendar?year=${currentYear}&month=${currentMonth}`);
    } catch (err) {
      alert("Error saving race goal");
    }
  };

  // Build grid of days
  const firstDayOfMonth = new Date(currentYear, currentMonth - 1, 1).getDay();
  // adjust to Monday start (0=Mon, 6=Sun)
  const mondayOffset = (firstDayOfMonth + 6) % 7;
  const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();

  const activitiesByDate: Record<string, any[]> = {};
  (calendar?.activities || []).forEach((a) => {
    activitiesByDate[a.date] = activitiesByDate[a.date] || [];
    activitiesByDate[a.date].push(a);
  });

  const goalsByDate: Record<string, any[]> = {};
  (calendar?.goals || []).forEach((g) => {
    if (g.date) {
      goalsByDate[g.date] = goalsByDate[g.date] || [];
      goalsByDate[g.date].push(g);
    }
  });

  const monthName = new Date(currentYear, currentMonth - 1, 1).toLocaleString("default", { month: "long" });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Training Calendar & Race Goals</h1>
          <p className="text-sm text-gray-400">
            Completed workouts, scheduled training blocks, and race milestones.
          </p>
        </div>

        <button
          onClick={() => setGoalModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-gray-950 transition shadow"
        >
          <Plus className="h-4 w-4" />
          <span>Add Race Goal</span>
        </button>
      </div>

      {/* Calendar Header Controls */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CalendarIcon className="h-5 w-5 text-cyan-400" />
          <h2 className="text-base font-bold text-white">
            {monthName} {currentYear}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={prevMonth}
            className="p-1.5 rounded-lg border border-gray-800 hover:bg-gray-800 text-gray-300 transition"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={nextMonth}
            className="p-1.5 rounded-lg border border-gray-800 hover:bg-gray-800 text-gray-300 transition"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-[#0C1220] border border-gray-800 rounded-xl overflow-hidden">
        {/* Day headers */}
        <div className="grid grid-cols-7 border-b border-gray-800 bg-gray-900/60 text-center text-xs font-medium text-gray-400 py-3">
          <span>MON</span>
          <span>TUE</span>
          <span>WED</span>
          <span>THU</span>
          <span>FRI</span>
          <span>SAT</span>
          <span>SUN</span>
        </div>

        {/* Days grid */}
        <div className="grid grid-cols-7 auto-rows-fr divide-x divide-y divide-gray-800">
          {/* Empty cells before 1st of month */}
          {Array.from({ length: mondayOffset }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-[100px] bg-gray-950/40 p-2" />
          ))}

          {/* Month days */}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const dayNum = i + 1;
            const isoDate = `${currentYear}-${String(currentMonth).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
            const acts = activitiesByDate[isoDate] || [];
            const goals = goalsByDate[isoDate] || [];

            const isToday =
              today.getFullYear() === currentYear &&
              today.getMonth() + 1 === currentMonth &&
              today.getDate() === dayNum;

            return (
              <div
                key={`day-${dayNum}`}
                className={`min-h-[110px] p-2 flex flex-col justify-between transition hover:bg-gray-800/30 ${
                  isToday ? "bg-cyan-950/20 border-t-2 border-t-cyan-400" : "bg-transparent"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`text-xs font-semibold ${
                      isToday ? "h-6 w-6 rounded-full bg-cyan-400 text-gray-950 flex items-center justify-center" : "text-gray-400"
                    }`}
                  >
                    {dayNum}
                  </span>
                  {acts.length > 0 && (
                    <span className="text-[10px] text-emerald-400 font-mono">
                      {acts.reduce((sum, a) => sum + (a.distance_km || 0), 0).toFixed(1)} km
                    </span>
                  )}
                </div>

                {/* Day events badges */}
                <div className="space-y-1 mt-1.5 overflow-hidden">
                  {goals.map((g, idx) => (
                    <div
                      key={`goal-${idx}`}
                      className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 truncate flex items-center gap-1"
                    >
                      <Flag className="h-3 w-3 shrink-0" />
                      <span>{g.name}</span>
                    </div>
                  ))}

                  {acts.map((a, idx) => (
                    <div
                      key={`act-${idx}`}
                      className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 truncate"
                    >
                      {a.name || "Run"} {a.distance_km ? `(${a.distance_km}k)` : ""}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Add Race Goal Modal */}
      {goalModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0C1220] border border-gray-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-base font-bold text-white mb-1">Set New Race Goal</h3>
            <p className="text-xs text-gray-400 mb-5">
              The AI training coach uses this target to tailor weekly volume and workouts.
            </p>

            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">Race Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Berlin Marathon"
                  value={raceName}
                  onChange={(e) => setRaceName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-sm text-white focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-1">Race Date</label>
                  <input
                    type="date"
                    required
                    value={raceDate}
                    onChange={(e) => setRaceDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-sm text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-300 mb-1">Distance (km)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={distanceKm}
                    onChange={(e) => setDistanceKm(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-sm text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">Target Finish Time (HH:MM:SS)</label>
                <input
                  type="text"
                  placeholder="1:45:00"
                  value={targetTimeStr}
                  onChange={(e) => setTargetTimeStr(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-sm text-white focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-800">
                <button
                  type="button"
                  onClick={() => setGoalModalOpen(false)}
                  className="px-3 py-2 rounded-lg text-xs font-medium text-gray-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-gray-950 transition"
                >
                  Save Race Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

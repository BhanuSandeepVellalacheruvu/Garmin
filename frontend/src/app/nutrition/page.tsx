"use client";

import React, { useEffect, useState } from "react";
import {
  Utensils,
  Droplet,
  Flame,
  Plus,
  Target,
  Sparkles,
  PieChart,
  Trash2,
  CheckCircle,
} from "lucide-react";
import { MetricDetailChart, DataPoint } from "@/components/charts/MetricDetailChart";
import { fetchAPI } from "@/lib/api";

interface DailySummary {
  date: string;
  calories: number;
  target_calories: number;
  calories_pct: number;
  water_ml: number;
  target_water_ml: number;
  water_pct: number;
  protein_g: number;
  target_protein_g: number;
  carbs_g: number;
  target_carbs_g: number;
  fat_g: number;
  target_fat_g: number;
}

export default function NutritionPage() {
  const [summary, setSummary] = useState<DailySummary[]>([]);
  const [targets, setTargets] = useState<any>({
    calories: 2200,
    water_ml: 2500,
    protein_g: 140,
    carbs_g: 250,
    fat_g: 70,
  });
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [foodName, setFoodName] = useState("");
  const [mealType, setMealType] = useState("snack");
  const [cals, setCals] = useState("350");
  const [protein, setProtein] = useState("25");
  const [carbs, setCarbs] = useState("40");
  const [fat, setFat] = useState("10");
  const [water, setWater] = useState("500");
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sumRes, entRes, tarRes] = await Promise.all([
        fetchAPI<{ targets: any; days: DailySummary[] }>("/nutrition/summary?days=14"),
        fetchAPI<any[]>("/nutrition/entries"),
        fetchAPI<any>("/nutrition/target"),
      ]);
      setSummary(sumRes.days || []);
      setTargets(tarRes || sumRes.targets);
      setEntries(entRes || []);
    } catch (err) {
      console.error("Failed to load nutrition data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!foodName.trim()) return;

    try {
      setSubmitting(true);
      await fetchAPI("/nutrition/entries", {
        method: "POST",
        body: JSON.stringify({
          entry_date: new Date().toISOString().split("T")[0],
          meal_type: mealType,
          food_name: foodName,
          calories: parseFloat(cals) || 0,
          protein_g: parseFloat(protein) || 0,
          carbs_g: parseFloat(carbs) || 0,
          fat_g: parseFloat(fat) || 0,
          water_ml: parseFloat(water) || 0,
        }),
      });
      setFoodName("");
      await loadData();
    } catch (err) {
      console.error("Failed to create entry:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteEntry = async (id: string) => {
    try {
      await fetchAPI(`/nutrition/entries/${id}`, { method: "DELETE" });
      setEntries(entries.filter((e) => e.id !== id));
      await loadData();
    } catch (err) {
      console.error("Failed to delete entry:", err);
    }
  };

  // Construct 10 Individual Chart Datasets
  const calorieData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: d.calories,
  }));

  const hydrationData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: d.water_ml,
  }));

  const proteinData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: d.protein_g,
  }));

  const carbsData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: d.carbs_g,
  }));

  const fatData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: d.fat_g,
  }));

  const deficitData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: Math.round(d.calories - (targets.target_calories || 2200)),
  }));

  const waterPctData: DataPoint[] = summary.map((d) => ({
    date: d.date,
    value: Math.round(d.water_pct),
  }));

  const proteinRatioData: DataPoint[] = summary.map((d) => {
    const totalCal = d.calories || 1;
    const pct = Math.round(((d.protein_g * 4) / totalCal) * 100);
    return { date: d.date, value: Math.min(100, Math.max(0, pct)) };
  });

  const carbRatioData: DataPoint[] = summary.map((d) => {
    const totalCal = d.calories || 1;
    const pct = Math.round(((d.carbs_g * 4) / totalCal) * 100);
    return { date: d.date, value: Math.min(100, Math.max(0, pct)) };
  });

  const fatRatioData: DataPoint[] = summary.map((d) => {
    const totalCal = d.calories || 1;
    const pct = Math.round(((d.fat_g * 9) / totalCal) * 100);
    return { date: d.date, value: Math.min(100, Math.max(0, pct)) };
  });

  // Current today values
  const todaySummary = summary[summary.length - 1];
  const curCal = todaySummary ? todaySummary.calories : 0;
  const curWater = todaySummary ? todaySummary.water_ml : 0;
  const curProtein = todaySummary ? todaySummary.protein_g : 0;
  const curCarbs = todaySummary ? todaySummary.carbs_g : 0;
  const curFat = todaySummary ? todaySummary.fat_g : 0;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-1.5">
              <Utensils className="w-3.5 h-3.5" /> Garmin Connect+ Nutrition & Hydration
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Nutrition & Hydration Tracking
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            10 dedicated, interactive metric charts tracking metabolic fuel, macro ratios, and
            electrolyte hydration.
          </p>
        </div>

        {/* Quick Targets Badge */}
        <div className="flex items-center gap-3 bg-[#101726] border border-gray-800 px-4 py-2 rounded-xl text-xs">
          <div className="text-right">
            <span className="text-gray-400 block text-[10px] uppercase font-mono">Daily Calorie Target</span>
            <span className="font-bold text-cyan-400 font-mono text-sm">
              {targets.target_calories || 2200} kcal
            </span>
          </div>
          <div className="h-6 w-px bg-gray-800" />
          <div className="text-right">
            <span className="text-gray-400 block text-[10px] uppercase font-mono">Water Target</span>
            <span className="font-bold text-blue-400 font-mono text-sm">
              {targets.target_water_ml || 2500} ml
            </span>
          </div>
        </div>
      </div>

      {/* Log Food & Hydration Drawer */}
      <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Plus className="w-4 h-4 text-cyan-400" /> Log Meal, Snack or Hydration
        </h3>
        <form onSubmit={handleAddEntry} className="grid grid-cols-2 md:grid-cols-7 gap-3">
          <div className="col-span-2">
            <label className="text-[10px] font-mono text-gray-400 uppercase block mb-1">
              Food / Drink Name
            </label>
            <input
              type="text"
              placeholder="e.g. Oatmeal & Banana, Electrolyte Mix"
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              required
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Meal</label>
            <select
              value={mealType}
              onChange={(e) => setMealType(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
              <option value="hydration">Hydration</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Calories</label>
            <input
              type="number"
              value={cals}
              onChange={(e) => setCals(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Protein (g)</label>
            <input
              type="number"
              value={protein}
              onChange={(e) => setProtein(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Water (ml)</label>
            <input
              type="number"
              value={water}
              onChange={(e) => setWater(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs py-2 rounded-lg transition disabled:opacity-50"
            >
              {submitting ? "Saving..." : "Add Entry"}
            </button>
          </div>
        </form>
      </div>

      {/* 10 Individual Dedicated Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Chart 1: Calories */}
        <MetricDetailChart
          title="Daily Caloric Intake"
          description="Total calories logged vs configured metabolic target"
          currentValue={curCal}
          unit="kcal"
          data={calorieData}
          type="area"
          color="cyan"
          icon={Flame}
          badge={`Target: ${targets.target_calories || 2200}`}
        />

        {/* Chart 2: Hydration */}
        <MetricDetailChart
          title="Hydration & Fluid Intake"
          description="Total water & electrolyte volume logged"
          currentValue={curWater}
          unit="ml"
          data={hydrationData}
          type="bar"
          color="blue"
          icon={Droplet}
          badge={`Target: ${targets.target_water_ml || 2500}ml`}
        />

        {/* Chart 3: Protein */}
        <MetricDetailChart
          title="Protein Intake"
          description="Dietary protein for muscle repair and recovery"
          currentValue={curProtein}
          unit="g"
          data={proteinData}
          type="line"
          color="emerald"
          icon={Utensils}
          badge={`Target: ${targets.target_protein_g || 140}g`}
        />

        {/* Chart 4: Carbs */}
        <MetricDetailChart
          title="Carbohydrates Intake"
          description="Muscle glycogen replenishing fuel"
          currentValue={curCarbs}
          unit="g"
          data={carbsData}
          type="line"
          color="amber"
          icon={Utensils}
          badge={`Target: ${targets.target_carbs_g || 250}g`}
        />

        {/* Chart 5: Fat */}
        <MetricDetailChart
          title="Dietary Fat Intake"
          description="Essential fatty acids and sustained cellular energy"
          currentValue={curFat}
          unit="g"
          data={fatData}
          type="line"
          color="rose"
          icon={Utensils}
          badge={`Target: ${targets.target_fat_g || 70}g`}
        />

        {/* Chart 6: Caloric Balance */}
        <MetricDetailChart
          title="Caloric Deficit / Surplus"
          description="Net variance against baseline daily metabolic target"
          currentValue={curCal - (targets.target_calories || 2200)}
          unit="kcal"
          data={deficitData}
          type="bar"
          color="violet"
          icon={Target}
        />

        {/* Chart 7: Water Completion % */}
        <MetricDetailChart
          title="Hydration Completion %"
          description="Percentage of daily hydration quota achieved"
          currentValue={todaySummary ? Math.round(todaySummary.water_pct) : 0}
          unit="%"
          data={waterPctData}
          type="area"
          color="blue"
          icon={Droplet}
          badgeVariant="success"
        />

        {/* Chart 8: Protein Calorie Ratio */}
        <MetricDetailChart
          title="Protein Macro Ratio"
          description="Percentage of daily caloric intake derived from protein"
          currentValue={todaySummary ? Math.round(((curProtein * 4) / (curCal || 1)) * 100) : 25}
          unit="%"
          data={proteinRatioData}
          type="line"
          color="emerald"
          icon={PieChart}
        />

        {/* Chart 9: Carb Macro Ratio */}
        <MetricDetailChart
          title="Carbohydrate Macro Ratio"
          description="Percentage of daily caloric intake derived from carbs"
          currentValue={todaySummary ? Math.round(((curCarbs * 4) / (curCal || 1)) * 100) : 50}
          unit="%"
          data={carbRatioData}
          type="line"
          color="amber"
          icon={PieChart}
        />

        {/* Chart 10: Fat Macro Ratio */}
        <MetricDetailChart
          title="Dietary Fat Macro Ratio"
          description="Percentage of daily caloric intake derived from fats"
          currentValue={todaySummary ? Math.round(((curFat * 9) / (curCal || 1)) * 100) : 25}
          unit="%"
          data={fatRatioData}
          type="line"
          color="rose"
          icon={PieChart}
        />
      </div>

      {/* Recent Entries Table */}
      <div className="bg-[#101726] border border-gray-800 rounded-2xl p-6">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider mb-4">
          Logged Entries (Past 7 Days)
        </h3>
        {entries.length === 0 ? (
          <p className="text-xs text-gray-500 py-4">No recent food or drink entries logged yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-gray-400 border-b border-gray-800 font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Meal</th>
                  <th className="py-2.5 px-3">Item</th>
                  <th className="py-2.5 px-3 text-right">Calories</th>
                  <th className="py-2.5 px-3 text-right">Protein</th>
                  <th className="py-2.5 px-3 text-right">Carbs</th>
                  <th className="py-2.5 px-3 text-right">Water</th>
                  <th className="py-2.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-medium">
                {entries.map((e) => (
                  <tr key={e.id} className="hover:bg-gray-900/40 text-gray-300">
                    <td className="py-2.5 px-3 font-mono">{e.entry_date}</td>
                    <td className="py-2.5 px-3 capitalize">
                      <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                        {e.meal_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-white">{e.food_name}</td>
                    <td className="py-2.5 px-3 text-right font-mono text-cyan-400">
                      {e.calories} kcal
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono">{e.protein_g}g</td>
                    <td className="py-2.5 px-3 text-right font-mono">{e.carbs_g}g</td>
                    <td className="py-2.5 px-3 text-right font-mono text-blue-400">
                      {e.water_ml} ml
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <button
                        onClick={() => handleDeleteEntry(e.id)}
                        className="text-gray-500 hover:text-rose-400 p-1 transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Footprints,
  Heart,
  Calendar,
  ListFilter,
  Brain,
  Settings,
  Activity,
  Sparkles,
  Utensils,
  Radio,
  Compass,
  Award,
  CalendarRange,
  Flame,
  Target,
} from "lucide-react";
import { cn } from "@/lib/utils";

const CORE_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/insights", label: "Active Intelligence", icon: Sparkles, badge: "AI" },
  { href: "/running", label: "Running Analytics", icon: Footprints },
  { href: "/health", label: "Health & Recovery", icon: Heart },
  { href: "/training", label: "Training & Load", icon: Target },
  { href: "/activities", label: "Activity Explorer", icon: ListFilter },
  { href: "/calendar", label: "Training Calendar", icon: Calendar },
  { href: "/coach", label: "AI Training Coach", icon: Brain },
];

const CONNECT_PLUS_ITEMS = [
  { href: "/nutrition", label: "Nutrition & Water", icon: Utensils },
  { href: "/live", label: "Live Activity", icon: Radio, pulse: true },
  { href: "/trails", label: "Route Explorer", icon: Compass },
  { href: "/badges", label: "Badges & Milestones", icon: Award },
  { href: "/rundown", label: "Year in Review", icon: CalendarRange },
  { href: "/offers", label: "Connect+ Perks", icon: Flame },
  { href: "/settings", label: "Settings & Sync", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-gray-800 bg-[#0B0F19] flex flex-col justify-between shrink-0 h-screen sticky top-0 overflow-y-auto">
      <div>
        {/* Brand header */}
        <div className="h-16 flex items-center px-6 border-b border-gray-800 gap-3">
          <div className="h-9 w-9 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="font-bold text-sm tracking-wide text-white">GARMIN AI</h1>
              <span className="text-[10px] font-bold bg-gradient-to-r from-cyan-500 to-blue-500 text-black px-1.5 py-0.2 rounded font-mono">
                +
              </span>
            </div>
            <p className="text-[10px] text-gray-400 tracking-wider font-mono">PERFORMANCE LAB</p>
          </div>
        </div>

        {/* Core Navigation */}
        <div className="p-3">
          <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
            Core Analytics
          </div>
          <nav className="space-y-0.5">
            {CORE_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition",
                    isActive
                      ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm"
                      : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/40"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Connect+ Features */}
          <div className="px-3 pt-4 pb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
            Connect+ Features
          </div>
          <nav className="space-y-0.5">
            {CONNECT_PLUS_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition",
                    isActive
                      ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm"
                      : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/40"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{item.label}</span>
                  </div>
                  {item.pulse && (
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer info */}
      <div className="p-4 border-t border-gray-800/80 text-[11px] text-gray-500 flex items-center justify-between">
        <span className="font-mono">v1.2.0 • Connect+</span>
        <div className="h-2 w-2 rounded-full bg-emerald-500" title="Connected" />
      </div>
    </aside>
  );
}

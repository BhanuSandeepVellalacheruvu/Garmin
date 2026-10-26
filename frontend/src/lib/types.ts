export interface Activity {
  id: string;
  garmin_activity_id: string;
  name: string | null;
  sport_type: string;
  activity_type: string | null;
  start_time: string;
  duration_seconds: number | null;
  distance_meters: number | null;
  avg_heart_rate: number | null;
  max_heart_rate: number | null;
  avg_speed_ms: number | null;
  elevation_gain: number | null;
  avg_cadence: number | null;
  calories: number | null;
  training_effect_aerobic: number | null;
  is_demo: boolean;
  laps?: ActivityLap[];
}

export interface ActivityLap {
  lap_index: number;
  duration_seconds: number | null;
  distance_meters: number | null;
  avg_heart_rate: number | null;
  avg_speed_ms: number | null;
  avg_cadence: number | null;
  elevation_gain: number | null;
}

export interface ActivitySample {
  timestamp: string;
  heart_rate: number | null;
  speed_ms: number | null;
  cadence: number | null;
  altitude: number | null;
  lat: number | null;
  lon: number | null;
}

export interface DailyHealthMetric {
  calendar_date: string;
  steps: number | null;
  resting_heart_rate: number | null;
  avg_stress_level: number | null;
  body_battery_high: number | null;
  body_battery_low: number | null;
  active_minutes: number | null;
  respiration_avg: number | null;
  is_demo: boolean;
}

export interface SleepRecord {
  calendar_date: string;
  total_sleep_seconds: number | null;
  deep_sleep_seconds: number | null;
  light_sleep_seconds: number | null;
  rem_sleep_seconds: number | null;
  awake_seconds?: number | null;
  sleep_score: number | null;
  hrv_last_night: number | null;
  hrv_last_night_5min_high?: number | null;
  hrv_weekly_avg: number | null;
  is_demo: boolean;
}

export interface HealthOverview {
  date: string;
  steps: number | null;
  resting_heart_rate: number | null;
  avg_stress_level: number | null;
  body_battery_high: number | null;
  body_battery_low: number | null;
  sleep_total_seconds: number | null;
  sleep_score: number | null;
  hrv_last_night: number | null;
  is_demo: boolean;
}

export interface GarminStatus {
  provider: string;
  is_demo_mode: boolean;
  capabilities: string[];
  last_sync: string | null;
  last_sync_status: string;
  last_sync_records: number;
  last_sync_error: string | null;
  configured: boolean;
}

export interface WeeklyVolume {
  this_week_km: number | null;
  last_week_km: number | null;
  weekly_volumes: { week_start: string; distance_km: number | null }[];
  run_type_distribution: Record<string, number>;
}

export interface TrainingLoad {
  acute_load_7d: number;
  chronic_load_28d: number;
  acwr: number | null;
  status: "optimal" | "high_risk" | "low" | "insufficient_data";
  note: string;
}

export interface Recommendation {
  category: "workout" | "recovery" | "volume" | "caution";
  title: string;
  rationale: string;
  action: string;
  confidence: "high" | "moderate" | "low";
  caveat: string;
}

export interface AIBriefing {
  date: string;
  summary: string;
  weekly_km: number;
  sleep_score: number | null;
  hrv: number | null;
}

export interface CalendarEvent {
  year: number;
  month: number;
  activities: {
    id: string;
    date: string;
    name: string | null;
    sport_type: string;
    distance_km: number | null;
    duration_s: number | null;
  }[];
  planned_days: {
    id: string;
    date: string;
    workout_type: string | null;
    description: string | null;
    target_distance_km: number | null;
    completed: boolean;
  }[];
  goals: {
    id: string;
    name: string;
    date: string | null;
    distance_km: number | null;
  }[];
}

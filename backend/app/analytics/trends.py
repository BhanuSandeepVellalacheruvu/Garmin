"""Rolling average and trend detection utilities."""
from __future__ import annotations

from statistics import mean, stdev


def rolling_avg(values: list[float | None], window: int) -> list[float | None]:
    """N-period rolling average. Returns None for windows with no data."""
    result = []
    for i in range(len(values)):
        window_vals = [v for v in values[max(0, i - window + 1): i + 1] if v is not None]
        result.append(round(mean(window_vals), 3) if window_vals else None)
    return result


def detect_trend(values: list[float | None], recent_n: int = 4) -> str:
    """Returns 'improving', 'declining', or 'stable' based on recent vs older average."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2 * recent_n:
        return "stable"
    recent = mean(vals[-recent_n:])
    older = mean(vals[-2 * recent_n: -recent_n])
    if older == 0:
        return "stable"
    pct = (recent - older) / older
    if pct > 0.03:
        return "improving"
    if pct < -0.03:
        return "declining"
    return "stable"


def week_over_week_change(now: float | None, prev: float | None) -> float | None:
    if now is None or prev is None or prev == 0:
        return None
    return round((now - prev) / prev * 100, 1)

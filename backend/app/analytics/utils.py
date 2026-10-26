"""Shared units and timezone utilities."""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_tz(dt: datetime, tz_str: str) -> datetime:
    try:
        return dt.astimezone(ZoneInfo(tz_str))
    except Exception:
        return dt.astimezone(timezone.utc)


def ms_to_min_per_km(speed_ms: float | None) -> float | None:
    """Convert m/s to min/km. Returns None for zero/None speed."""
    if not speed_ms or speed_ms <= 0:
        return None
    return 1000 / (speed_ms * 60)


def ms_to_min_per_mile(speed_ms: float | None) -> float | None:
    if not speed_ms or speed_ms <= 0:
        return None
    return 1609.344 / (speed_ms * 60)


def format_pace(speed_ms: float | None, unit: str = "km") -> str:
    """Return pace string like '5:30 /km'."""
    conv = ms_to_min_per_km if unit == "km" else ms_to_min_per_mile
    val = conv(speed_ms)
    if val is None:
        return "—"
    mins = int(val)
    secs = int((val - mins) * 60)
    return f"{mins}:{secs:02d} /{unit}"


def meters_to_km(m: float | None) -> float | None:
    return round(m / 1000, 2) if m is not None else None


def meters_to_miles(m: float | None) -> float | None:
    return round(m / 1609.344, 2) if m is not None else None


def seconds_to_hms(s: float | None) -> str:
    if s is None:
        return "—"
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h {m}m {sec}s" if h else f"{m}m {sec}s"

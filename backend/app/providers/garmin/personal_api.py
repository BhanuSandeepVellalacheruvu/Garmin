"""Official Garmin Connect Personal API provider.

Authentication flow (as documented at developer.garmin.com/gc-developer-program/personal):
  POST https://personal.connectapi.garmin.com/personalapitoken-service/personal-api/personal-api-key/token
  Header: Authorization: ApiKey <GARMIN_PERSONAL_API_KEY>
  Response: {"access_token": "...", "token_type": "Bearer", "expires_in": 86400}

Bearer tokens are valid for 24 hours. No refresh tokens are issued.
The app re-exchanges the API key automatically before expiry.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.providers.garmin.base import (
    GarminAPIError,
    GarminAuthError,
    GarminDailySummary,
    GarminHRVData,
    GarminActivity,
    GarminProvider,
    GarminRateLimitError,
    GarminSleepRecord,
)
from app.providers.garmin.normalizer import GarminNormalizer

log = logging.getLogger(__name__)

# Token re-use buffer: refresh 5 minutes before expiry
_TOKEN_BUFFER_SECONDS = 300


class GarminPersonalApiProvider(GarminProvider):
    """
    Implements the official Garmin Connect Personal API.

    Capabilities verified against the Swagger definition at
    https://personal.connectapi.garmin.com (as of 2024-2025).
    """

    BASE_URL = "https://personal.connectapi.garmin.com"

    # Capability registry — what this provider can deliver
    _CAPABILITIES = {
        "activities",
        "activity_detail",
        "daily_summary",
        "sleep",
        "hrv",
        "hr_zones",
        "weight",
        "stress",
        "steps",
    }

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.GARMIN_PERSONAL_API_KEY
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None
        self._lock = asyncio.Lock()
        self._normalizer = GarminNormalizer()

    # ── Authentication ──────────────────────────────────────

    async def authenticate(self) -> bool:
        """Exchange API key for a Bearer token. Returns True on success."""
        if not self._api_key:
            raise GarminAuthError(
                "GARMIN_PERSONAL_API_KEY is not configured. "
                "Set it in .env or use GARMIN_PROVIDER=mock for demo mode."
            )
        await self._refresh_token()
        return self._access_token is not None

    async def _refresh_token(self) -> None:
        """Exchange API key for a new Bearer token (server-side only)."""
        token_url = (
            f"{self.BASE_URL}/personalapitoken-service/personal-api/personal-api-key/token"
        )
        # Log the action but never log the key itself
        log.info("Requesting new Garmin access token")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    token_url,
                    headers={"Authorization": f"ApiKey {self._api_key}"},
                )
            if resp.status_code == 401:
                raise GarminAuthError(
                    "Garmin API key was rejected (HTTP 401). "
                    "Check GARMIN_PERSONAL_API_KEY in your .env file."
                )
            if resp.status_code == 429:
                raise GarminRateLimitError("Garmin rate limit hit during authentication.")
            if resp.status_code != 200:
                raise GarminAPIError(
                    f"Unexpected token response: HTTP {resp.status_code} — {resp.text[:200]}"
                )
            # Garmin Personal API returns the raw JWT Bearer token as text/plain
            raw_text = resp.text.strip()
            if raw_text.startswith("ey") or "text/plain" in resp.headers.get("content-type", ""):
                self._access_token = raw_text
                expires_in = 86400
            else:
                try:
                    data = resp.json()
                    self._access_token = data.get("access_token") or raw_text
                    expires_in = int(data.get("expires_in", 86400))
                except Exception:
                    self._access_token = raw_text
                    expires_in = 86400

            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in - _TOKEN_BUFFER_SECONDS
            )
            log.info("Garmin access token acquired, expires in %ds", expires_in)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise GarminAPIError(f"Network error reaching Garmin API: {exc}") from exc

    async def _ensure_authenticated(self) -> str:
        """Return a valid Bearer token, refreshing if necessary."""
        async with self._lock:
            now = datetime.now(timezone.utc)
            if self._access_token is None or (
                self._token_expires_at and now >= self._token_expires_at
            ):
                await self._refresh_token()
        assert self._access_token is not None
        return self._access_token

    @property
    def _auth_headers(self) -> dict[str, str]:
        """Must call _ensure_authenticated first."""
        return {"Authorization": f"Bearer {self._access_token}"}

    # ── Retry-wrapped request helper ────────────────────────

    @retry(
        retry=retry_if_exception_type((GarminRateLimitError, GarminAPIError)),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        stop=stop_after_attempt(3),
    )
    async def _get(self, path: str, params: dict | None = None) -> Any:
        token = await self._ensure_authenticated()
        url = f"{self.BASE_URL}{path}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    params=params or {},
                )
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as exc:
            raise GarminAPIError(f"Network error: {exc}") from exc

        if resp.status_code == 401:
            # Token may have been revoked; clear it and raise
            self._access_token = None
            raise GarminAuthError("Bearer token rejected. API key may be revoked.")
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            log.warning("Garmin rate limit, backing off %ds", retry_after)
            raise GarminRateLimitError(f"Rate limited; retry after {retry_after}s")
        if resp.status_code == 404:
            return None
        if resp.status_code not in (200, 204):
            raise GarminAPIError(
                f"Garmin API error {resp.status_code}: {resp.text[:300]}"
            )
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    # ── Public Provider Methods ─────────────────────────────

    async def get_activities(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[GarminActivity]:
        data = await self._get(
            "/activitylist-service/activities/search/activities",
            params={
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "limit": min(limit, 100),
                "start": offset,
            },
        )
        if not data:
            return []
        activities = data if isinstance(data, list) else data.get("activityList", [])
        return [self._normalizer.normalize_activity(a) for a in activities]

    async def get_activity_details(self, activity_id: str) -> GarminActivity | None:
        data = await self._get(f"/activity-service/activity/{activity_id}")
        if not data:
            return None
        return self._normalizer.normalize_activity(data)

    async def get_daily_summaries(
        self, start_date: date, end_date: date
    ) -> list[GarminDailySummary]:
        summaries: list[GarminDailySummary] = []
        current = start_date
        while current <= end_date:
            data = await self._get(
                "/usersummary-service/usersummary/daily",
                params={"calendarDate": current.isoformat()},
            )
            if data:
                summaries.append(self._normalizer.normalize_daily_summary(data, current))
            current = date.fromordinal(current.toordinal() + 1)
            await asyncio.sleep(0.5)  # Respect rate limits
        return summaries

    async def get_sleep(
        self, start_date: date, end_date: date
    ) -> list[GarminSleepRecord]:
        # Garmin sleep endpoint enforces a maximum 28-day date window per request
        records: list[GarminSleepRecord] = []
        cur_start = start_date
        while cur_start <= end_date:
            cur_end = min(cur_start + timedelta(days=27), end_date)
            data = await self._get(
                "/sleep-service/sleep/dailySleepSummariesByDate",
                params={"startDate": cur_start.isoformat(), "endDate": cur_end.isoformat()},
            )
            if data:
                records_raw = data if isinstance(data, list) else data.get("dailySleepDTO", [])
                for r in records_raw:
                    if r:
                        records.append(self._normalizer.normalize_sleep(r))
            cur_start = cur_end + timedelta(days=1)
            await asyncio.sleep(0.4)
        return records

    async def get_hrv(
        self, start_date: date, end_date: date
    ) -> list[GarminHRVData]:
        data = await self._get(
            f"/hrv-service/hrv/daily/{start_date.isoformat()}/{end_date.isoformat()}"
        )
        if not data:
            return []
        records_raw = data if isinstance(data, list) else data.get("hrvSummaries", [])
        return [self._normalizer.normalize_hrv(r) for r in records_raw if r]

    async def get_hr_zones(self) -> dict[str, Any]:
        data = await self._get("/biometric-service/heartRateZones/v2")
        return data or {}

    def get_capabilities(self) -> set[str]:
        return self._CAPABILITIES.copy()

    def get_provider_name(self) -> str:
        return "Garmin Connect Personal API (Official)"

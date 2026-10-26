"""Provider factory — returns the configured Garmin provider."""
from app.core.config import settings
from app.providers.garmin.base import GarminProvider


def get_garmin_provider() -> GarminProvider:
    if settings.GARMIN_PROVIDER == "official":
        from app.providers.garmin.personal_api import GarminPersonalApiProvider
        return GarminPersonalApiProvider()
    elif settings.GARMIN_PROVIDER == "mock":
        from app.providers.garmin.mock import MockGarminProvider
        return MockGarminProvider()
    else:
        raise ValueError(f"Unknown GARMIN_PROVIDER: {settings.GARMIN_PROVIDER!r}. Use 'official' or 'mock'.")

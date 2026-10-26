from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

# Search for .env in project root, then backend directory, then current directory
_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
_ROOT_ENV = _BASE_DIR / ".env"
_BACKEND_ENV = _BASE_DIR / "backend" / ".env"

_env_files = [f for f in [_ROOT_ENV, _BACKEND_ENV, Path(".env")] if f.exists()] or [".env"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_files, extra="ignore")

    # App
    APP_ENV: Literal["development", "production", "test"] = "development"
    APP_SECRET_KEY: str = "change-me-in-production"
    LOG_LEVEL: str = "INFO"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./garmin.db"

    # Garmin
    GARMIN_PROVIDER: Literal["official", "compatible", "mock"] = "mock"
    GARMIN_PERSONAL_API_KEY: str = ""
    GARMIN_API_BASE_URL: str = "https://personal.connectapi.garmin.com"
    GARMIN_TOKEN_ENDPOINT: str = "/personalapitoken-service/personal-api/personal-api-key/token"
    SYNC_INTERVAL_MINUTES: int = 60

    # LLM
    LLM_PROVIDER: Literal["ollama", "openai_compatible", "mock"] = "mock"
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "llama3.2"

    # Redis (optional)
    REDIS_URL: str = ""


settings = Settings()


"""
Application Configuration and Environment Variables
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "AuraCast"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Defaults
    DEFAULT_CITY: str = "Kolkata"
    DEFAULT_LAT: float = 22.5726
    DEFAULT_LON: float = 88.3639
    DEFAULT_COUNTRY: str = "IN"
    
    # API Keys & Secrets (Must be provided via environment variables)
    OPENWEATHER_API_KEY: str = ""
    
    # External API Base URLs
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_GEO_URL: str = "https://api.openweathermap.org/geo/1.0"
    OPENMETEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    OPENMETEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPENMETEO_GEO_URL: str = "https://geocoding-api.open-meteo.com/v1"
    
    # Service Constraints
    HISTORICAL_DAYS: int = 30
    HTTP_TIMEOUT_SECONDS: float = 10.0
    
    # Machine Learning Settings
    ML_N_ESTIMATORS: int = 60
    ML_RANDOM_STATE: int = 42
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

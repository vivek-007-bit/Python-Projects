"""
Master Weather Orchestrator Service
Coordinates Geocoding, Current Weather, Real Historical Observations, and ML Pipeline.
Supports Progressive Loading (Instant Current Weather + Asynchronous ML Prediction).
"""

import logging
import time
from typing import Optional, Dict, Tuple
from app.config import settings
from app.models.location import LocationInfo
from app.models.weather import WeatherBundleResponse, CurrentWeatherResponse
from app.models.prediction import PredictionBundleResponse
from app.services.geocoding import geocoding_service
from app.services.openweather import openweather_service
from app.services.historical import historical_service
from app.ml.models import ml_pipeline

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        # In-memory TTL cache for serverless warm execution: key -> (timestamp, data)
        self._bundle_cache: Dict[str, Tuple[float, WeatherBundleResponse]] = {}
        self._current_cache: Dict[str, Tuple[float, CurrentWeatherResponse]] = {}
        self._prediction_cache: Dict[str, Tuple[float, PredictionBundleResponse]] = {}
        self._cache_ttl_seconds = 600  # 10 minutes cache

    def _get_cache_key(self, lat: float, lon: float) -> str:
        return f"{round(lat, 2)}:{round(lon, 2)}"

    async def resolve_location(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> LocationInfo:
        """Resolve geographical coordinates and location info."""
        if city and city.strip():
            locations = await geocoding_service.search_locations(city.strip())
            if not locations:
                raise ValueError(f"City '{city}' could not be resolved to geographical coordinates.")
            top_loc = locations[0]
            return LocationInfo(
                city=top_loc.name,
                country=top_loc.country,
                state=top_loc.state,
                latitude=top_loc.latitude,
                longitude=top_loc.longitude
            )
        elif lat is not None and lon is not None:
            return await geocoding_service.resolve_coordinates(lat, lon)
        else:
            return LocationInfo(
                city=settings.DEFAULT_CITY,
                country=settings.DEFAULT_COUNTRY,
                latitude=settings.DEFAULT_LAT,
                longitude=settings.DEFAULT_LON
            )

    async def get_current_weather_bundle(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> CurrentWeatherResponse:
        """
        Fast, lightweight current weather retrieval.
        Returns location, live OpenWeather observation, and 24-hour baseline forecast in <200ms.
        """
        location = await self.resolve_location(city=city, lat=lat, lon=lon)
        cache_key = self._get_cache_key(location.latitude, location.longitude)
        now_ts = time.time()

        if cache_key in self._current_cache:
            saved_ts, cached_resp = self._current_cache[cache_key]
            if now_ts - saved_ts < self._cache_ttl_seconds:
                cached_resp.location = location
                return cached_resp

        # 1. Fetch Current Weather
        current_weather, is_fallback = await openweather_service.get_current_weather(location)

        # 2. Fetch 24-Hour Baseline Hourly Forecast
        hourly_forecast = await historical_service.get_hourly_forecast_baseline(
            location.latitude,
            location.longitude
        )

        fallback_msg = (
            "OpenWeather API key not detected or rate-limited. Using Open-Meteo as high-precision fallback."
            if is_fallback else None
        )

        response = CurrentWeatherResponse(
            status="success",
            location=location,
            current=current_weather,
            hourly_forecast=hourly_forecast,
            is_fallback=is_fallback,
            message=fallback_msg
        )

        self._current_cache[cache_key] = (now_ts, response)
        return response

    async def get_prediction_bundle(
        self,
        lat: float,
        lon: float
    ) -> PredictionBundleResponse:
        """
        Location-specific machine learning prediction pipeline.
        Fetches 30-day historical observations, extracts features, trains models, and returns predictions.
        """
        cache_key = self._get_cache_key(lat, lon)
        now_ts = time.time()

        if cache_key in self._prediction_cache:
            saved_ts, cached_resp = self._prediction_cache[cache_key]
            if now_ts - saved_ts < self._cache_ttl_seconds:
                return cached_resp

        # 1. Fetch Real Historical Weather Data
        hist_df, hist_summary = await historical_service.get_historical_dataframe(lat, lon)

        # 2. Train & Predict using Real Historical Data in ML Pipeline
        prediction_result = ml_pipeline.train_and_predict(hist_df)

        response = PredictionBundleResponse(
            status="success",
            prediction=prediction_result,
            historical=hist_summary.model_dump()
        )

        self._prediction_cache[cache_key] = (now_ts, response)
        return response

    async def get_complete_weather_bundle(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> WeatherBundleResponse:
        """
        Complete monolithic weather retrieval and ML prediction pipeline.
        Preserved for backward compatibility.
        """
        location = await self.resolve_location(city=city, lat=lat, lon=lon)
        cache_key = self._get_cache_key(location.latitude, location.longitude)
        now_ts = time.time()

        if cache_key in self._bundle_cache:
            saved_ts, cached_resp = self._bundle_cache[cache_key]
            if now_ts - saved_ts < self._cache_ttl_seconds:
                cached_resp.location = location
                return cached_resp

        current_weather, is_fallback = await openweather_service.get_current_weather(location)
        hist_df, hist_summary = await historical_service.get_historical_dataframe(location.latitude, location.longitude)
        hourly_forecast = await historical_service.get_hourly_forecast_baseline(location.latitude, location.longitude)
        prediction_result = ml_pipeline.train_and_predict(hist_df)

        fallback_msg = (
            "OpenWeather API key not detected or rate-limited. Using Open-Meteo as high-precision fallback."
            if is_fallback else None
        )

        bundle = WeatherBundleResponse(
            status="success",
            location=location,
            current=current_weather,
            historical=hist_summary,
            prediction=prediction_result,
            hourly_forecast=hourly_forecast,
            is_fallback=is_fallback,
            message=fallback_msg
        )

        self._bundle_cache[cache_key] = (now_ts, bundle)
        return bundle


weather_service = WeatherService()

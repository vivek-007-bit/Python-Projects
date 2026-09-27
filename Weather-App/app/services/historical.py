"""
Historical Weather Service using Open-Meteo Historical & Archive API
Retrieves real chronological observations for the selected latitude and longitude.
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
import httpx
import pandas as pd
from app.config import settings
from app.models.location import LocationInfo
from app.models.weather import HistoricalDataSummary, HistoricalDataPoint, HourlyForecastItem
from app.services.openweather import map_condition_icon

logger = logging.getLogger(__name__)


class HistoricalWeatherService:
    def __init__(self):
        self.timeout = settings.HTTP_TIMEOUT_SECONDS
        self.days = settings.HISTORICAL_DAYS

    async def get_historical_dataframe(self, lat: float, lon: float) -> Tuple[pd.DataFrame, HistoricalDataSummary]:
        """
        Fetch real past 30-day hourly weather observations for the coordinates.
        Returns cleaned pandas DataFrame and structured HistoricalDataSummary.
        """
        # We query the Open-Meteo API for past 30 days of hourly observations
        url = settings.OPENMETEO_FORECAST_URL
        params = {
            "latitude": lat,
            "longitude": lon,
            "past_days": self.days,
            "forecast_days": 1,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "surface_pressure",
                "precipitation",
                "rain",
                "wind_speed_10m",
                "wind_direction_10m",
                "cloud_cover",
                "weather_code"
            ],
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        if not times:
            raise ValueError(f"No historical hourly data returned for coordinates ({lat}, {lon})")

        # Create DataFrame
        df = pd.DataFrame({
            "time": pd.to_datetime(times),
            "temperature": hourly.get("temperature_2m", []),
            "humidity": hourly.get("relative_humidity_2m", []),
            "pressure": hourly.get("surface_pressure", []),
            "precipitation": hourly.get("precipitation", []),
            "rain": hourly.get("rain", []),
            "wind_speed": hourly.get("wind_speed_10m", []),
            "wind_direction": hourly.get("wind_direction_10m", []),
            "cloud_cover": hourly.get("cloud_cover", []),
            "weather_code": hourly.get("weather_code", [])
        })

        # Ensure sorted chronologically and drop any NaNs
        df = df.sort_values("time").reset_index(drop=True)
        df = df.ffill().bfill()

        # Compute summary statistics for the past observations
        now = pd.Timestamp.now()
        past_mask = df["time"] <= now
        past_df = df[past_mask] if past_mask.any() else df

        avg_temp = round(float(past_df["temperature"].mean()), 1)
        min_temp = round(float(past_df["temperature"].min()), 1)
        max_temp = round(float(past_df["temperature"].max()), 1)
        avg_hum = round(float(past_df["humidity"].mean()), 1)
        total_precip = round(float(past_df["precipitation"].sum()), 1)

        # Sample recent 24-48 hours for trend chart
        recent_records = past_df.tail(48)
        trend_points = [
            HistoricalDataPoint(
                time=row["time"].strftime("%b %d, %H:00"),
                temperature=round(float(row["temperature"]), 1),
                humidity=int(row["humidity"]),
                pressure=round(float(row["pressure"]), 1),
                precipitation=round(float(row["precipitation"]), 1),
                wind_speed=round(float(row["wind_speed"]), 1)
            )
            for _, row in recent_records.iterrows()
        ]

        summary = HistoricalDataSummary(
            days_retrieved=self.days,
            data_points_count=len(past_df),
            avg_temperature=avg_temp,
            min_temperature=min_temp,
            max_temperature=max_temp,
            avg_humidity=avg_hum,
            total_precipitation=total_precip,
            recent_trend=trend_points,
            source="Open-Meteo Historical Archive"
        )

        return df, summary

    async def get_hourly_forecast_baseline(self, lat: float, lon: float) -> List[HourlyForecastItem]:
        """Fetch upcoming 24-hour hourly forecast from Open-Meteo as baseline."""
        url = settings.OPENMETEO_FORECAST_URL
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": 2,
            "hourly": [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "precipitation_probability",
                "weather_code"
            ],
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                temps = hourly.get("temperature_2m", [])
                feels = hourly.get("apparent_temperature", [])
                hums = hourly.get("relative_humidity_2m", [])
                probs = hourly.get("precipitation_probability", [])
                codes = hourly.get("weather_code", [])

                now = datetime.now()
                items: List[HourlyForecastItem] = []
                for i, t_str in enumerate(times):
                    dt = datetime.fromisoformat(t_str)
                    if dt >= now - timedelta(hours=1) and len(items) < 24:
                        code = codes[i] if i < len(codes) else 0
                        cond_name = "Rain" if code >= 50 else ("Clouds" if code >= 1 else "Clear")
                        items.append(
                            HourlyForecastItem(
                                time=dt.strftime("%H:00"),
                                datetime_iso=t_str,
                                temperature=round(float(temps[i]), 1) if i < len(temps) else 20.0,
                                feels_like=round(float(feels[i]), 1) if i < len(feels) else None,
                                humidity=int(hums[i]) if i < len(hums) else 50,
                                precipitation_prob=float(probs[i]) if i < len(probs) and probs[i] is not None else 0.0,
                                condition=cond_name,
                                icon=map_condition_icon(cond_name)
                            )
                        )
                return items
        return []


historical_service = HistoricalWeatherService()

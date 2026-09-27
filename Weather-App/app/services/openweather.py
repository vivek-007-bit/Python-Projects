"""
Current Weather Service fetching observations from OpenWeatherMap
with seamless Open-Meteo fallback for resilience.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
import httpx
from app.config import settings
from app.models.location import LocationInfo
from app.models.weather import CurrentWeather, WeatherMetrics

logger = logging.getLogger(__name__)

COMPASS_POINTS = [
    ('N', 0, 11.25), ('NNE', 11.25, 33.75), ('NE', 33.75, 56.25), ('ENE', 56.25, 78.75),
    ('E', 78.75, 101.25), ('ESE', 101.25, 123.75), ('SE', 123.75, 146.25), ('SSE', 146.25, 168.75),
    ('S', 168.75, 191.25), ('SSW', 191.25, 213.75), ('SW', 213.75, 236.25), ('WSW', 236.25, 258.75),
    ('W', 258.75, 281.25), ('WNW', 281.25, 303.75), ('NW', 303.75, 326.25), ('NNW', 326.25, 348.75),
    ('N', 348.75, 360.0)
]


def degrees_to_compass(deg: float) -> str:
    """Convert degree angle (0-360) to 16-point compass direction."""
    norm_deg = deg % 360
    for name, start, end in COMPASS_POINTS:
        if start <= norm_deg < end:
            return name
    return "N"


def map_condition_icon(condition: str) -> str:
    """Map meteorological condition text to crisp UI icon keys."""
    c = condition.lower()
    if "clear" in c or "sunny" in c:
        return "sunny"
    if "cloud" in c or "overcast" in c:
        return "cloudy"
    if "rain" in c or "drizzle" in c or "shower" in c:
        return "rainy"
    if "thunder" in c or "storm" in c:
        return "thunderstorm"
    if "snow" in c or "blizzard" in c or "ice" in c:
        return "snow"
    if "fog" in c or "mist" in c or "haze" in c or "smoke" in c:
        return "fog"
    return "partly_cloudy"


class OpenWeatherService:
    def __init__(self):
        self.timeout = settings.HTTP_TIMEOUT_SECONDS

    async def get_current_weather(self, location: LocationInfo) -> Tuple[CurrentWeather, bool]:
        """
        Fetch current weather metrics for a location.
        Returns (CurrentWeather, is_fallback_flag).
        """
        if settings.OPENWEATHER_API_KEY:
            try:
                weather = await self._fetch_openweather(location.latitude, location.longitude)
                if weather:
                    return weather, False
            except Exception as e:
                logger.warning(f"OpenWeatherMap request failed: {e}. Falling back to Open-Meteo.")

        # Fallback to Open-Meteo
        weather = await self._fetch_openmeteo(location.latitude, location.longitude)
        return weather, True

    async def _fetch_openweather(self, lat: float, lon: float) -> Optional[CurrentWeather]:
        url = f"{settings.OPENWEATHER_BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": settings.OPENWEATHER_API_KEY
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                main = data.get("main", {})
                wind = data.get("wind", {})
                weather_info = data.get("weather", [{}])[0]
                sys = data.get("sys", {})
                
                wind_deg = int(wind.get("deg", 0))
                condition = weather_info.get("main", "Clear")
                description = weather_info.get("description", "Clear sky").title()
                
                sunrise_ts = sys.get("sunrise")
                sunset_ts = sys.get("sunset")
                sunrise_str = datetime.fromtimestamp(sunrise_ts, tz=timezone.utc).strftime("%H:%M") if sunrise_ts else None
                sunset_str = datetime.fromtimestamp(sunset_ts, tz=timezone.utc).strftime("%H:%M") if sunset_ts else None
                
                metrics = WeatherMetrics(
                    temperature=round(float(main.get("temp", 0.0)), 1),
                    feels_like=round(float(main.get("feels_like", main.get("temp", 0.0))), 1),
                    temp_min=round(float(main.get("temp_min", main.get("temp", 0.0))), 1),
                    temp_max=round(float(main.get("temp_max", main.get("temp", 0.0))), 1),
                    humidity=int(main.get("humidity", 50)),
                    pressure=round(float(main.get("pressure", 1013.25)), 1),
                    wind_speed=round(float(wind.get("speed", 0.0)), 1),
                    wind_direction_deg=wind_deg,
                    wind_direction_compass=degrees_to_compass(wind_deg),
                    cloudiness=int(data.get("clouds", {}).get("all", 0)),
                    visibility=round(float(data.get("visibility", 10000)) / 1000.0, 1),
                )
                
                return CurrentWeather(
                    condition=condition,
                    description=description,
                    icon=map_condition_icon(condition),
                    metrics=metrics,
                    sunrise=sunrise_str,
                    sunset=sunset_str,
                    observed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    source="OpenWeatherMap"
                )
        return None

    async def _fetch_openmeteo(self, lat: float, lon: float) -> CurrentWeather:
        url = settings.OPENMETEO_FORECAST_URL
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m",
                "cloud_cover",
                "weather_code"
            ],
            "daily": ["sunrise", "sunset", "temperature_2m_max", "temperature_2m_min"],
            "timezone": "auto"
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            curr = data.get("current", {})
            daily = data.get("daily", {})
            
            wind_deg = int(curr.get("wind_direction_10m", 0))
            wcode = curr.get("weather_code", 0)
            condition, desc = self._decode_wmo_code(wcode)
            
            temp_min = daily.get("temperature_2m_min", [curr.get("temperature_2m", 20)])[0]
            temp_max = daily.get("temperature_2m_max", [curr.get("temperature_2m", 20)])[0]
            
            sunrise = daily.get("sunrise", [None])[0]
            sunset = daily.get("sunset", [None])[0]
            sunrise_str = sunrise.split("T")[-1] if sunrise and "T" in sunrise else sunrise
            sunset_str = sunset.split("T")[-1] if sunset and "T" in sunset else sunset
            
            metrics = WeatherMetrics(
                temperature=round(float(curr.get("temperature_2m", 20.0)), 1),
                feels_like=round(float(curr.get("apparent_temperature", curr.get("temperature_2m", 20.0))), 1),
                temp_min=round(float(temp_min), 1),
                temp_max=round(float(temp_max), 1),
                humidity=int(curr.get("relative_humidity_2m", 50)),
                pressure=round(float(curr.get("surface_pressure", 1013.25)), 1),
                wind_speed=round(float(curr.get("wind_speed_10m", 0.0)) / 3.6, 1),  # km/h to m/s
                wind_direction_deg=wind_deg,
                wind_direction_compass=degrees_to_compass(wind_deg),
                cloudiness=int(curr.get("cloud_cover", 0)),
                visibility=10.0,
            )
            
            return CurrentWeather(
                condition=condition,
                description=desc,
                icon=map_condition_icon(condition),
                metrics=metrics,
                sunrise=sunrise_str,
                sunset=sunset_str,
                observed_at=curr.get("time", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
                source="Open-Meteo"
            )

    @staticmethod
    def _decode_wmo_code(code: int) -> Tuple[str, str]:
        """Decode WMO Weather Interpretation Codes (0-99)."""
        if code == 0:
            return "Clear", "Clear sky"
        elif code in (1, 2):
            return "Clouds", "Mainly clear or partly cloudy"
        elif code == 3:
            return "Clouds", "Overcast"
        elif code in (45, 48):
            return "Fog", "Fog and depositing rime fog"
        elif code in (51, 53, 55):
            return "Rain", "Drizzle: light to dense intensity"
        elif code in (61, 63, 65):
            return "Rain", "Rain: slight to heavy intensity"
        elif code in (71, 73, 75, 77):
            return "Snow", "Snow fall or snow grains"
        elif code in (80, 81, 82):
            return "Rain", "Rain showers"
        elif code in (95, 96, 99):
            return "Thunderstorm", "Thunderstorm with or without hail"
        return "Clouds", "Partly cloudy"


openweather_service = OpenWeatherService()

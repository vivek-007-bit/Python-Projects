"""
Geocoding Service for Resolving Locations (City Search & Reverse Coordinates)
Supports OpenWeather Geocoding and Open-Meteo Geocoding Fallback
"""

import logging
from typing import List, Optional
import httpx
from app.config import settings
from app.models.location import LocationInfo, GeocodingResult

logger = logging.getLogger(__name__)


class GeocodingService:
    def __init__(self):
        self.timeout = settings.HTTP_TIMEOUT_SECONDS

    async def search_locations(self, query: str) -> List[GeocodingResult]:
        """Search for matching cities given a text query."""
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()
        results: List[GeocodingResult] = []

        # Try OpenWeather Geocoding if API key is provided
        if settings.OPENWEATHER_API_KEY:
            try:
                results = await self._search_openweather(query)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"OpenWeather geocoding failed: {e}. Falling back to Open-Meteo.")

        # Fallback to Open-Meteo Geocoding (Free, no key required)
        try:
            results = await self._search_openmeteo(query)
        except Exception as e:
            logger.error(f"Open-Meteo geocoding failed: {e}")

        return results

    async def resolve_coordinates(self, lat: float, lon: float) -> LocationInfo:
        """Resolve location name from latitude and longitude coordinates."""
        # Try OpenWeather Reverse Geocoding
        if settings.OPENWEATHER_API_KEY:
            try:
                info = await self._reverse_openweather(lat, lon)
                if info:
                    return info
            except Exception as e:
                logger.warning(f"OpenWeather reverse geocoding failed: {e}")

        # Fallback to Open-Meteo Reverse Geocoding / Timezone determination
        try:
            info = await self._reverse_openmeteo(lat, lon)
            if info:
                return info
        except Exception as e:
            logger.warning(f"Open-Meteo reverse geocoding failed: {e}")

        # Default fallback if all resolution fails
        return LocationInfo(
            city=f"Location ({lat:.2f}, {lon:.2f})",
            country="Global",
            latitude=lat,
            longitude=lon,
            timezone="UTC"
        )

    async def _search_openweather(self, query: str) -> List[GeocodingResult]:
        url = f"{settings.OPENWEATHER_GEO_URL}/direct"
        params = {
            "q": query,
            "limit": 5,
            "appid": settings.OPENWEATHER_API_KEY
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    GeocodingResult(
                        name=item.get("name", query),
                        country=item.get("country", ""),
                        state=item.get("state"),
                        latitude=item["lat"],
                        longitude=item["lon"]
                    )
                    for item in data if "lat" in item and "lon" in item
                ]
        return []

    async def _search_openmeteo(self, query: str) -> List[GeocodingResult]:
        url = f"{settings.OPENMETEO_GEO_URL}/search"
        params = {
            "name": query,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                return [
                    GeocodingResult(
                        name=item.get("name", query),
                        country=item.get("country_code", item.get("country", "")),
                        state=item.get("admin1"),
                        latitude=item["latitude"],
                        longitude=item["longitude"]
                    )
                    for item in results if "latitude" in item and "longitude" in item
                ]
        return []

    async def _reverse_openweather(self, lat: float, lon: float) -> Optional[LocationInfo]:
        url = f"{settings.OPENWEATHER_GEO_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "limit": 1,
            "appid": settings.OPENWEATHER_API_KEY
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    item = data[0]
                    return LocationInfo(
                        city=item.get("name", "Unknown City"),
                        country=item.get("country", ""),
                        state=item.get("state"),
                        latitude=lat,
                        longitude=lon
                    )
        return None

    async def _reverse_openmeteo(self, lat: float, lon: float) -> Optional[LocationInfo]:
        # Using Open-Meteo elevation/timezone lookup or coordinate naming
        url = f"{settings.OPENMETEO_FORECAST_URL}"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "timezone": "auto"
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                tz = data.get("timezone", "UTC")
                tz_city = tz.split("/")[-1].replace("_", " ") if "/" in tz else "Current Location"
                return LocationInfo(
                    city=tz_city,
                    country=tz.split("/")[0] if "/" in tz else "Earth",
                    latitude=lat,
                    longitude=lon,
                    timezone=tz
                )
        return None


geocoding_service = GeocodingService()

"""
API Route for Weather Observations & Progressive Loading
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.weather import WeatherBundleResponse, CurrentWeatherResponse
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name to search (e.g., 'Kolkata', 'London', 'Tokyo')"),
    lat: Optional[float] = Query(None, description="Geographic latitude coordinate"),
    lon: Optional[float] = Query(None, description="Geographic longitude coordinate")
):
    """
    Retrieve fast, lightweight current weather and 24-hour baseline forecast.
    Enables instant Progressive Loading without waiting for ML training.
    """
    try:
        result = await weather_service.get_current_weather_bundle(city=city, lat=lat, lon=lon)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve current weather: {str(e)}")


@router.get("", response_model=WeatherBundleResponse)
async def get_weather(
    city: Optional[str] = Query(None, description="City name to search (e.g., 'Kolkata', 'London', 'Tokyo')"),
    lat: Optional[float] = Query(None, description="Geographic latitude coordinate"),
    lon: Optional[float] = Query(None, description="Geographic longitude coordinate")
):
    """
    Retrieve monolithic complete weather bundle (current + historical + predictions).
    Preserved for backward compatibility.
    """
    try:
        result = await weather_service.get_complete_weather_bundle(city=city, lat=lat, lon=lon)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve weather data: {str(e)}")

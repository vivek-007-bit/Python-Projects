"""
Weather Data Pydantic Models
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.location import LocationInfo
from app.models.prediction import PredictionResult


class WeatherMetrics(BaseModel):
    temperature: float = Field(..., description="Current temperature in °C")
    feels_like: float = Field(..., description="Apparent temperature in °C")
    temp_min: float = Field(..., description="Minimum recorded temperature in °C")
    temp_max: float = Field(..., description="Maximum recorded temperature in °C")
    humidity: int = Field(..., description="Relative humidity percentage (0-100)")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction_deg: int = Field(..., description="Wind direction in degrees (0-360)")
    wind_direction_compass: str = Field("N", description="16-point compass direction (e.g. NW, ENE)")
    cloudiness: int = Field(0, description="Cloudiness percentage (0-100)")
    visibility: Optional[float] = Field(None, description="Visibility in kilometers")
    dew_point: Optional[float] = Field(None, description="Dew point in °C")
    uv_index: Optional[float] = Field(None, description="UV Index")


class CurrentWeather(BaseModel):
    condition: str = Field(..., description="Main weather condition category (e.g., Clear, Clouds, Rain)")
    description: str = Field(..., description="Detailed condition description")
    icon: str = Field("cloudy", description="Normalized icon identifier")
    metrics: WeatherMetrics
    sunrise: Optional[str] = Field(None, description="Formatted local sunrise time")
    sunset: Optional[str] = Field(None, description="Formatted local sunset time")
    observed_at: str = Field(..., description="ISO or formatted timestamp of observation")
    source: str = Field("OpenWeatherMap", description="Data source provider")


class HourlyForecastItem(BaseModel):
    time: str = Field(..., description="Formatted timestamp (e.g., '14:00')")
    datetime_iso: str
    temperature: float
    feels_like: Optional[float] = None
    humidity: int
    precipitation_prob: Optional[float] = None
    condition: str = "Clear"
    icon: str = "sunny"


class HistoricalDataPoint(BaseModel):
    time: str
    temperature: float
    humidity: int
    pressure: float
    precipitation: float
    wind_speed: float


class HistoricalDataSummary(BaseModel):
    days_retrieved: int
    data_points_count: int
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    total_precipitation: float
    recent_trend: List[HistoricalDataPoint]
    source: str = "Open-Meteo Historical Archive"


class CurrentWeatherResponse(BaseModel):
    status: str = "success"
    location: LocationInfo
    current: CurrentWeather
    hourly_forecast: List[HourlyForecastItem]
    is_fallback: bool = False
    message: Optional[str] = None


class WeatherBundleResponse(BaseModel):
    status: str = "success"
    location: LocationInfo
    current: CurrentWeather
    historical: HistoricalDataSummary
    prediction: PredictionResult
    hourly_forecast: List[HourlyForecastItem]
    is_fallback: bool = False
    message: Optional[str] = None

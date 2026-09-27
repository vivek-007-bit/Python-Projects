"""
Location and Geocoding Pydantic Models
"""

from typing import Optional
from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    city: str = Field(..., description="Name of the city")
    country: str = Field(..., description="Country code or country name")
    state: Optional[str] = Field(None, description="State or province if available")
    latitude: float = Field(..., description="Geographic latitude coordinate")
    longitude: float = Field(..., description="Geographic longitude coordinate")
    timezone: Optional[str] = Field(None, description="Local timezone string")


class GeocodingResult(BaseModel):
    name: str
    country: str
    state: Optional[str] = None
    latitude: float
    longitude: float

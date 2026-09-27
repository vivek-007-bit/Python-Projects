"""
API Route for Location Search & Reverse Geocoding
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models.location import LocationInfo, GeocodingResult
from app.services.geocoding import geocoding_service

router = APIRouter(prefix="/api/location", tags=["location"])


@router.get("/search", response_model=List[GeocodingResult])
async def search_cities(
    q: str = Query(..., min_length=2, description="City query string")
):
    """Search for matching cities and geographic coordinates."""
    try:
        results = await geocoding_service.search_locations(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location search failed: {str(e)}")


@router.get("/reverse", response_model=LocationInfo)
async def reverse_lookup(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate")
):
    """Resolve city name from coordinates."""
    try:
        return await geocoding_service.resolve_coordinates(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse geocoding failed: {str(e)}")

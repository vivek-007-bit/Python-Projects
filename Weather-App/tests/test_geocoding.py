"""
Test Suite for Geocoding and Location Resolution
"""

import pytest
from app.services.geocoding import geocoding_service


@pytest.mark.asyncio
async def test_search_locations():
    results = await geocoding_service.search_locations("London")
    assert len(results) > 0
    top = results[0]
    assert "london" in top.name.lower()
    assert -90.0 <= top.latitude <= 90.0
    assert -180.0 <= top.longitude <= 180.0


@pytest.mark.asyncio
async def test_resolve_coordinates():
    loc = await geocoding_service.resolve_coordinates(22.5726, 88.3639)
    assert loc.latitude == 22.5726
    assert loc.longitude == 88.3639
    assert loc.city is not None

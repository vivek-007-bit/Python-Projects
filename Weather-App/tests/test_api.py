"""
Test Suite for FastAPI Endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "app_name" in data


@pytest.mark.asyncio
async def test_home_page_html():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "AuraCast" in resp.text
        assert "text/html" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_model_docs_page_html():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/model-docs")
        assert resp.status_code == 200
        assert "How Our Weather Prediction Model Works" in resp.text
        assert "RandomForest" in resp.text
        assert "text/html" in resp.headers["content-type"]



@pytest.mark.asyncio
async def test_location_search_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/location/search?q=Tokyo")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "tokyo" in data[0]["name"].lower()


@pytest.mark.asyncio
async def test_weather_bundle_api_default():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/weather?city=Kolkata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "location" in data
        assert "current" in data
        assert "historical" in data
        assert "prediction" in data
        assert "hourly_forecast" in data
        assert 0.0 <= data["prediction"]["rain_probability_next_24h"] <= 100.0


@pytest.mark.asyncio
async def test_current_weather_api_fast():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/weather/current?city=Kolkata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "location" in data
        assert "current" in data
        assert "hourly_forecast" in data
        # Prediction & historical should not be in current weather payload (progressive loading)
        assert "prediction" not in data
        assert "historical" not in data


@pytest.mark.asyncio
async def test_prediction_bundle_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/prediction?lat=22.57&lon=88.36")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "prediction" in data
        assert "historical" in data
        assert 0.0 <= data["prediction"]["rain_probability_next_24h"] <= 100.0


@pytest.mark.asyncio
async def test_static_assets_serving():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test CSS
        css_resp = await client.get("/static/css/custom.css")
        assert css_resp.status_code == 200
        assert "skeleton" in css_resp.text

        # Test JS
        js_resp = await client.get("/static/js/app.js")
        assert js_resp.status_code == 200
        assert "DOMContentLoaded" in js_resp.text

        # Test SVG Icon
        icon_resp = await client.get("/static/icons/cloudy.svg")
        assert icon_resp.status_code == 200
        assert "<svg" in icon_resp.text



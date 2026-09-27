"""
Application Health Check Route
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    """Health check endpoint for uptime monitors and serverless probes."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "openweather_configured": bool(settings.OPENWEATHER_API_KEY)
    }

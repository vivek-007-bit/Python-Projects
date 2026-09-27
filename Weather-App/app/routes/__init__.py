"""
Routes Package
"""

from app.routes.pages import router as pages_router
from app.routes.weather import router as weather_router
from app.routes.prediction import router as prediction_router
from app.routes.location import router as location_router
from app.routes.health import router as health_router

__all__ = [
    "pages_router",
    "weather_router",
    "prediction_router",
    "location_router",
    "health_router"
]

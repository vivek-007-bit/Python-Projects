"""
Root entrypoint for Vercel zero-configuration detection and local ASGI runners.
Exposes the FastAPI application instance from app.main.
"""
from app.main import app

__all__ = ["app"]

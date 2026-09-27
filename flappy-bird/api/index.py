"""
Vercel Serverless Function entrypoint.
Exposes the FastAPI application instance as 'app'.
"""
from app.main import app

# Export for Vercel ASGI serverless runtime
__all__ = ["app"]

"""
FastAPI Main Application Entry Point
Configures middleware, routes, static asset serving, and global exception handlers.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import (
    pages_router,
    weather_router,
    prediction_router,
    location_router,
    health_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Create FastAPI application
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Modern Weather Intelligence & Location-Specific Machine Learning Prediction API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler (Never expose raw stack traces to clients)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal error occurred while processing the weather prediction request.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )

# Mount Static Files (Handles both local running and Vercel serverless path)
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register Routers
app.include_router(pages_router)
app.include_router(weather_router)
app.include_router(prediction_router)
app.include_router(location_router)
app.include_router(health_router)

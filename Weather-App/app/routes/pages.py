"""
Frontend HTML View Routes (Jinja2 Server-Side Rendering)
"""

from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(tags=["pages"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render main modern weather dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "default_city": settings.DEFAULT_CITY,
            "has_openweather_key": bool(settings.OPENWEATHER_API_KEY),
            "active_page": "weather"
        }
    )


@router.get("/model-docs", response_class=HTMLResponse)
async def model_docs_page(request: Request):
    """Render technical Machine Learning Model Documentation page."""
    return templates.TemplateResponse(
        request=request,
        name="model_docs.html",
        context={
            "app_name": settings.APP_NAME,
            "active_page": "model_docs"
        }
    )


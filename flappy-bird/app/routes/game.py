"""
Game routes serving the primary HTML5 Canvas interface and status endpoints.
"""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse, Response

router = APIRouter()

FAVICON_PATH = Path(__file__).resolve().parent.parent / "static" / "assets" / "images" / "bird.png"

@router.get("/", response_class=HTMLResponse)
async def get_game_page(request: Request):
    """Renders the primary Flappy Bird game page."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Flappy Bird — Web Edition",
            "version": "1.0.0"
        }
    )

@router.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """Serves the game icon for favicon requests to prevent 404s."""
    if FAVICON_PATH.is_file():
        return FileResponse(FAVICON_PATH, media_type="image/png")
    return Response(status_code=204)

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and uptime probes."""
    return {"status": "ok", "game": "Flappy Bird", "engine": "HTML5 Canvas"}


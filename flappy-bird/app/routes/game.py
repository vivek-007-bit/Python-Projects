"""
Game routes serving the primary HTML5 Canvas interface and status endpoints.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

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

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and uptime probes."""
    return {"status": "ok", "game": "Flappy Bird", "engine": "HTML5 Canvas"}

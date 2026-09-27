"""
Main FastAPI application entrypoint.
Serves the web-native Flappy Bird canvas game and static assets.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes.game import router as game_router

# Resolve absolute filesystem paths based on this file's directory
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

app = FastAPI(
    title="Flappy Bird Web Edition",
    description="Web-native Flappy Bird game powered by HTML5 Canvas, Vanilla JavaScript, and FastAPI.",
    version="1.0.0"
)

# Ensure static and template directories exist before mounting
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static asset directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates

# Register application routes
app.include_router(game_router)

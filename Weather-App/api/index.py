"""
Vercel Serverless Function Entry Point
Exposes the ASGI FastAPI app instance for Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add project root to sys.path so 'app' module is discoverable on Vercel
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app

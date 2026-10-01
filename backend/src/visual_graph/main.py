from fastapi import FastAPI

from visual_graph import __version__
from visual_graph.api import health
from visual_graph.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=__version__)
    app.include_router(health.router)
    return app
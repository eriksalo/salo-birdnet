import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.db.connection import open_db
from app.routers import api, audio, charts, config_page, dashboard, detections, species, system

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = Settings()
    app.state.settings = settings
    logger.info(f"Opening database: {settings.birdnet_db_path}")
    app.state.db = await open_db(settings)
    logger.info("Database connected")
    yield
    await app.state.db.close()
    logger.info("Database closed")


app = FastAPI(title="Salo BirdNET", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(detections.router)
app.include_router(species.router)
app.include_router(audio.router)
app.include_router(charts.router)
app.include_router(api.router)
app.include_router(config_page.router)
app.include_router(system.router)

if __name__ == "__main__":
    import uvicorn
    settings = Settings()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)

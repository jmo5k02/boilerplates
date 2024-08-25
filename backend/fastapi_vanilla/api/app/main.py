import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.src.api_core.project_logger import setup_logging
from app.src.api_core import deps, init_db
from app.settings import Settings

logger = logging.getLogger("app_core")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("./app/src/api_core/logging_config.json")
    logger.info("Starting application")
    logger.info("Initializing database")
    await init_db.create_tables()
    logger.info("application started")
    yield

app = FastAPI(
    lifespan=lifespan,
)


@app.get("/api/health")
async def get_health(settings: deps.SettingsDep):
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "testing": settings.testing
    }
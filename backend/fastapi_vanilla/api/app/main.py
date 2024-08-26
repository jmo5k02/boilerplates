import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.src.api_core.logging.project_logger import setup_logging
from app.src.api_core.routers import api_v1, health

logger = logging.getLogger("app_core")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Setting up logging")
    try:
        setup_logging("./app/src/api_core/logging/logging_config.json")
    except Exception as e:
        print(f"Error setting up logging: {e}")
        raise
    logger.info("Starting application")
    # logger.info("Initializing database")
    # await init_db.create_tables()
    logger.info("application started")
    yield
    logger.info("application shutting down")


def create_application() -> FastAPI:
    application = FastAPI(
        lifespan=lifespan,
    )
    application.include_router(health.router, prefix="/api", tags=["health"])
    application.include_router(api_v1.router, prefix="/api/v1", tags=["v1"])
    return application


app = create_application()

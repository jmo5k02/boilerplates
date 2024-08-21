import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute

import src.api.api_v1
from src.api.project_logger import setup_logging
from src.api.init_db import create_tables
from settings import global_settings, set_cors_origins, custom_generate_unique_id


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging("./src/_common/logging_config.json")
    logger.info("Starting application")
    logger.info("Creating tables")
    create_tables()
    logger.info("application started")
    yield


app = FastAPI(
    title=global_settings.PROJECT_NAME,
    # This is important so that the frontend can generate the client
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
)

if global_settings.BACKEND_CORS_ORIGINS:
    set_cors_origins(global_settings.BACKEND_CORS_ORIGINS, app)


@app.get("/health-check", tags=["health-check"])
def read_root(request: Request):
    client_ip = request.client.host
    logger.info("health-check from %s", client_ip)
    return {"Hello": "World"}


app.include_router(src.api.api_v1.router, prefix=global_settings.API_V1_STR, tags=["v1"])


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server")
    uvicorn.run("main:app", **{
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": bool(os.getenv("RELOAD", True)),
    })

import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.settings import Settings, get_settings
from app.db.manage import init_database
from app.extensions.logger import configure_logging
from app.api import api_router
from app.common.utils.cli import install_plugins


log = logging.getLogger(__name__)


configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up")
    log.info("Application starting up")
    await init_database(get_settings())
    yield
    log.info("Application shutting down")


def create_application(_settings: Settings, lifespan_func: Callable) -> FastAPI:
    application = FastAPI(
        title="FastAPI Vanilla Tenant Support",
        description="A FastAPI application with tenant support",
        version="0.1.0",
        lifespan=lifespan_func,
        openapi_url=_settings.OPENAPI_URL,
        docs_url=_settings.DOCS_URL,
    )

    # Middleware
    application.add_middleware(
        middleware_class=CORSMiddleware,
        **{
            "allow_origins": ["http://localhost:3000"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    ) 

    # Exception Handlers

    # Routers
    application.include_router(router=api_router, prefix="/api/v1", tags=["v1"])

    @application.get("/api/v1/healthcheck", status_code=status.HTTP_200_OK)
    async def healthcheck(request: Request):
        return {"status": "ok"}

    return application

app = create_application(get_settings(), lifespan)

print("Installing plugins")
install_plugins()

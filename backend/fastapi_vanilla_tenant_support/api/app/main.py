import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.db.manage import init_database
from app.extensions.logger import configure_logging
from app.api import api_router
from app.settings import settings
from app.common.utils.cli import install_plugins


log = logging.getLogger(__name__)


configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up")
    log.info("Application starting up")
    await init_database()
    yield
    log.info("Application shutting down")


def create_application() -> FastAPI:
    application = FastAPI(
        title="FastAPI Vanilla Tenant Support",
        description="A FastAPI application with tenant support",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
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

    @application.get("/redirect/{address}")
    async def redirect(address: str, request: Request):
        return RedirectResponse(f'http://{address}.de', status_code=status.HTTP_302_FOUND)

    return application

app = create_application()

print("Installing plugins")
install_plugins()

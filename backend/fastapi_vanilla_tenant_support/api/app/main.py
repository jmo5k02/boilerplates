import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.db.manage import init_database
from app.extensions.logger import configure_logging


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
    # application.include_router(router=auth_router, prefix="/{tenant}/auth", tags=["auth"])

    return application

app = create_application()

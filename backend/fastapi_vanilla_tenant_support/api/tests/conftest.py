import os

# Settings overrides
os.environ["TESTING"] = "1"
os.environ["ENVIRONMENT"] = "dev"
os.environ["PROJECT_NAME"] = "fastapi_vanilla_tenant_support"
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost,http://localhost:3000"
os.environ["POSTGRES_SERVER_HOST"] = "localhost"
os.environ["POSTGRES_SERVER_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from fastapi import FastAPI

from app.main import create_application
from app.settings import get_settings
from app.db.manage import init_database
from app.common.utils.sqlalchemy_utils import (
    create_database,
    database_exists,
    drop_database,
)

from tests.database import Session

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.TESTING,
    isolation_level="AUTOCOMMIT",
)

print(settings.SQLALCHEMY_DATABASE_URI)

@pytest.fixture(scope="session")
async def db():
    if await database_exists(str(settings.SQLALCHEMY_DATABASE_URI)):
        await drop_database(str(settings.SQLALCHEMY_DATABASE_URI))

    await init_database(settings)

    schema_engine = engine.execution_options(
        schema_translate_map={None: "app_tenant_default", "app_core": "app_core"}
    )
    Session.configure(bind=schema_engine)
    yield
    await schema_engine.dispose()
    await drop_database(str(settings.SQLALCHEMY_DATABASE_URI))

@pytest.fixture(scope="session", params=["asyncio", "trio"])
def anyio_backend(request):
    """Override anyio backend fixture to use session scope with both asyncio and trio"""
    return request.param

@pytest.fixture(scope="function", autouse=True)
async def session(db):
    """
    Creates a database session for test duration
    """
    async with Session() as s:
        yield s
    await s.rollback()


@pytest.fixture(scope="function")
async def client(session, ):
    app = create_application(settings, None)
    async with AsyncClient(
        transport=ASGITransport(app=app, root_path="/api/v1"),
        base_url="http://test/api/v1",
    ) as ac:
        yield ac



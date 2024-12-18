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

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from polyfactory.factories.sqlalchemy_factory import SQLAASyncPersistence

from app.main import create_application
from app.settings import get_settings
from app.db.manage import init_database
from app.common.utils.sqlalchemy_utils import (
    create_database,
    database_exists,
    drop_database,
)
from app.tenants.models import Tenant
from app.auth.models import AppUser, AppUserTenant
from app.db.engine import engine

from .database import Session
from .factories import UserFactory, TenantFactory, BaseFactory, UserTenantFactory

settings = get_settings()

print(settings.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="session")
async def db():
    print("Creating database")
    if await database_exists(str(settings.SQLALCHEMY_DATABASE_URI)):
        await drop_database(str(settings.SQLALCHEMY_DATABASE_URI))

    await init_database(settings)

    schema_engine = engine.execution_options(
        schema_translate_map={None: "app_tenant_default", "app_core": "app_core"}
    )

    Session.configure(bind=schema_engine)

    yield
    # await engine.dispose()
    await schema_engine.dispose()
    await drop_database(str(settings.SQLALCHEMY_DATABASE_URI))


@pytest.fixture(scope="session", params=["asyncio"])
def anyio_backend(request):
    """Override anyio backend fixture to use session scope with both asyncio and trio"""
    return request.param


@pytest.fixture(scope="function", autouse=True)
async def session(db):
    """
    Creates a database session for test duration
    """
    async with Session() as session:
        yield session
        await session.rollback()
    await Session.remove()


@pytest.fixture(scope="function")
async def client(
    session,
):
    app = create_application(settings, None)
    async with AsyncClient(
        transport=ASGITransport(app=app, root_path="/api/v1"),
        base_url="http://test/api/v1",
    ) as ac:
        yield ac


@pytest.fixture
async def tenant(session) -> Tenant:
    return await TenantFactory.create_async()


@pytest.fixture
async def user(session) -> Tenant:
    return await UserFactory.create_async()


@pytest.fixture
async def user_tenant(session) -> tuple[AppUser, Tenant]:
    user = await UserFactory.create_async()
    tenant = await TenantFactory.create_async()
    return user, tenant

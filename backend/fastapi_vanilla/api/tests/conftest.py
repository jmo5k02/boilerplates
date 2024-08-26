import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker

from app.main import create_application
from app.settings import Settings, get_settings
from app.src.api_core.db.database import Base, get_db
# Database model imports
from app.src.summaries.model import Summary
from app.src.users.model import User


def get_settings_override():
    return Settings(
        testing=1,
    )


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="module")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_engine(event_loop):
    """This function creates an database engine and returns it
    It also creates all tables that are imported at the top of this file"""
    engine: AsyncEngine = create_async_engine(
        os.getenv("POSTGRES_SERVER_TEST_URL"), echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    engine.sync_engine.dispose()


@pytest.fixture(scope="module")
async def db_session(
    db_engine: AsyncEngine,
) -> AsyncSession:
    """This function creates a new session for each test"""
    SessionLocal = sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with db_engine.connect() as conn:
        tsx = await conn.begin()
        async with SessionLocal(bind=conn) as session:
            nested_tsx = await conn.begin_nested()

            yield session

            if nested_tsx.is_active:
                await nested_tsx.rollback()
            await tsx.rollback()


@pytest.fixture(scope="module")
async def async_app_client(
    db_session: AsyncSession,
) -> AsyncClient:
    # set up
    appl = create_application()
    appl.dependency_overrides[get_settings] = get_settings_override

    async def override_get_db():
        try:
            yield db_session
        except Exception as e:
            await db_session.rollback()
            raise e
        finally:
            await db_session.close()

    appl.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=appl), base_url="http://test"
    ) as test_client:
        # testing
        yield test_client

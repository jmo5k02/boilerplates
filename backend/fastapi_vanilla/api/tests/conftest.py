import os

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import create_application
from app.settings import get_settings, Settings
from app.src.api_core.db.database import get_db, Base

# Database model imports
from app.src.users.model import User
from app.src.summaries.model import Summary


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


def setup_database_and_create_session(database_url: str,
                                             connect_args: dict = None
                                             ) -> Session:
    """This function creates an database engine and session
    It also creates all tables that are imported at the top of this file"""
    engine = create_engine(
        database_url,
        echo=True
    )
    session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )
    Base.metadata.create_all(engine)
    return session


@pytest.fixture(scope="module")
async def test_app_with_db():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    session = setup_database_and_create_session(
        os.getenv("POSTGRES_SERVER_TEST_URL")
    )
    def override_get_db():
        try:
            db = session()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # tear down
    pass


import pytest
from app.main import create_application
from httpx import AsyncClient, ASGITransport

def test_minimal_app(test_app_with_db):
    pass
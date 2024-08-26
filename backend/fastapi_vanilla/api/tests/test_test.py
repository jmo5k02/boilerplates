import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_application


def test_minimal_app():
    print("HELLO")

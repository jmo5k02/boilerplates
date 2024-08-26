import json
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_summary(async_app_client):
    response = await async_app_client.post(
        "/api/v1/summaries/",
        json={"url": "https://foo.bar"},
    )

    assert response.status_code == 201
    print(response.json())
    assert response.json()["url"] == "https://foo.bar/"


@pytest.mark.anyio
async def test_create_summary_invalid_json(async_app_client):
    response = await async_app_client.post(
        "/api/v1/summaries/",
        json={},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


@pytest.mark.anyio
async def test_create_summary_invalid_url(async_app_client):
    response = await async_app_client.post(
        "/api/v1/summaries/",
        json={"url": "invalid://url"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"expected_schemes": "'http' or 'https'"},
                "input": "invalid://url",
                "loc": ["body", "url"],
                "msg": "URL scheme should be 'http' or 'https'",
                "type": "url_scheme",
            }
        ]
    }


@pytest.mark.anyio
async def test_read_summary(async_app_client):
    response = await async_app_client.post(
        "/api/v1/summaries/",
        json={"url": "https://foo.bar"},
    )
    summary_id = response.json()["id"]

    response = await async_app_client.get(f"/api/v1/summaries/{summary_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": summary_id,
        "url": "https://foo.bar/",
        "summary": "This is a dummy summary",
    }


@pytest.mark.anyio
async def test_read_summary_incorrect_id(async_app_client):
    response = await async_app_client.get(f"/api/v1/summaries/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


@pytest.mark.anyio
async def test_read_all_summaries(async_app_client):
    response = await async_app_client.post(
        "/api/v1/summaries/",
        json={"url": "https://foo.bar"},
    )
    summary_id = response.json()["id"]
    response = await async_app_client.get(
        "/api/v1/summaries/",
    )
    assert response.status_code == 200
    assert len(list(filter(lambda d: d["id"] == summary_id, response.json()))) == 1

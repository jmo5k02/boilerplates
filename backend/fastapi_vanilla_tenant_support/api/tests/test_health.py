import pytest
import time

@pytest.mark.anyio
async def test_health(client):
    time.sleep(10)
    response = await client.get("/api/v1/healthcheck")
    reponse = await client.get("/api/v1/users")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
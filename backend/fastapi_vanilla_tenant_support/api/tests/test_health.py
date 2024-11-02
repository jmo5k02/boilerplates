import pytest
import time
@pytest.mark.anyio
async def test_health(client):
    response = await client.get("/api/v1/healthcheck")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    time.sleep(10)
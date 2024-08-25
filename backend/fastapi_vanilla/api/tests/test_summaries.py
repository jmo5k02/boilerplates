import json
import inspect
import pytest

@pytest.mark.asyncio
async def test_create_summary(test_app_with_db):
    # Given
    # test_app_with_db
    # print("Fixture:", await test_app_with_db.get('api/health'))
    # # When
    print('Pre post request')
    response = await test_app_with_db.post(
        "/api/v1/summaries/",
        json={"url": "https://foo.bar"},
    )

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar"
    


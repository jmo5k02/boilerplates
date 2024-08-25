from app import main


def test_health(test_app):
    # Given
    # test_app

    # When
    response = test_app.get("/api/health")

    # Then
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "dev", "testing": True}
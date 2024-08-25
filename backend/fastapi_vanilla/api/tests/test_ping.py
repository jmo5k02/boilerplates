from app import main


def test_ping(test_app):
    response = test_app.get("/api/health")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"status": "ok", "environment": "dev", "testing": True}
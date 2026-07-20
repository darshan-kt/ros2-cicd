from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_defaults_false_without_ros():
    response = client.get("/health")

    assert response.json() == {
        "publisher": False,
        "subscriber": False,
        "system": False,
    }


def test_reset_reports_failure_without_ros():
    response = client.post("/reset")

    assert response.status_code == 200
    assert response.json() == {"message": "reset failed"}


def test_cors_allows_frontend_origin():
    response = client.get(
        "/health", headers={"Origin": "http://localhost:8080"}
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"


def test_websocket_streams_counter_values():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()

        assert set(data.keys()) == {"publisher", "subscriber"}

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_is_up() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_bearer_token_authenticates() -> None:
    response = client.get(
        "/profile",
        headers={"Authorization": "Bearer demo-valid-token"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["name"] == "Ada Demo"


def test_invalid_token_is_rejected() -> None:
    response = client.get(
        "/profile",
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401

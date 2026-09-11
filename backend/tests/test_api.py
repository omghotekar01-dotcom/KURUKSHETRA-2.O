from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.repositories.incidents import IncidentStore


def test_create_list_and_get_incident(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "api.db"))
    client = TestClient(main_module.app)

    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 after deployment",
            "description": "Production users get 401 immediately after successful login.",
            "environment": "production",
            "logs": ["JWT signature verification failed"],
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["triage"]["component"] == "Authentication"
    assert created["status"] == "INVESTIGATING"
    assert len(created["timeline"]) == 2

    listed = client.get("/api/v1/incidents").json()
    assert listed[0]["id"] == created["id"]

    fetched = client.get(f"/api/v1/incidents/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["incident"]["title"] == "401 after deployment"


def test_missing_incident_returns_404(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "api.db"))
    client = TestClient(main_module.app)

    response = client.get("/api/v1/incidents/INC-DOES-NOT-EXIST")

    assert response.status_code == 404

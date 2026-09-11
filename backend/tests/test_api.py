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


def test_investigate_returns_runbook_evidence(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "api.db"))
    client = TestClient(main_module.app)
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 after deployment",
            "description": "Successful login is followed by unauthorized API responses.",
            "logs": ["JWT signature verification failed"],
        },
    ).json()

    response = client.post(f"/api/v1/incidents/{created['id']}/investigate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["matches"][0]["id"] == "RB-AUTH-001"

    updated = client.get(f"/api/v1/incidents/{created['id']}").json()
    assert updated["timeline"][-1]["stage"] == "EVIDENCE"

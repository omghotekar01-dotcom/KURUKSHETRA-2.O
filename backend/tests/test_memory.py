from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.repositories.incidents import IncidentStore


def test_verified_resolution_becomes_reusable_memory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "memory.db"))
    client = TestClient(main_module.app)

    first = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 after deployment",
            "description": "Successful login is followed by unauthorized API responses.",
            "logs": ["JWT signature verification failed"],
        },
    ).json()
    analysis = client.post(f"/api/v1/incidents/{first['id']}/analyze").json()
    client.post(
        f"/api/v1/incidents/{first['id']}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
        },
    )
    verification = client.post(
        f"/api/v1/incidents/{first['id']}/verify",
        json={
            "outcome": "PASS",
            "evidence": "Authenticated reproduction request returned 200 and JWT verification succeeded.",
            "checked_by": "demo-verifier",
        },
    )
    assert verification.status_code == 200

    memories = client.get("/api/v1/memory").json()
    assert len(memories) == 1
    assert memories[0]["incident_id"] == first["id"]
    assert memories[0]["source"] == "verified-resolution"
    assert "401" in memories[0]["symptoms"]

    second = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 again after a new deployment",
            "description": "Users sign in, then protected API requests return unauthorized.",
            "logs": ["JWT signature verification failed"],
        },
    ).json()
    second_analysis = client.post(f"/api/v1/incidents/{second['id']}/analyze").json()

    assert any(match["source"] == "verified-resolution" for match in second_analysis["evidence"]["matches"])


def test_failed_verification_does_not_enter_memory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "memory.db"))
    client = TestClient(main_module.app)

    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "Database timeout",
            "description": "Production database requests time out while saving profiles.",
            "logs": ["connection pool exhausted"],
        },
    ).json()
    analysis = client.post(f"/api/v1/incidents/{created['id']}/analyze").json()
    client.post(
        f"/api/v1/incidents/{created['id']}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
        },
    )
    client.post(
        f"/api/v1/incidents/{created['id']}/verify",
        json={
            "outcome": "FAIL",
            "evidence": "The reproduction request still times out.",
            "checked_by": "demo-verifier",
        },
    )

    assert client.get("/api/v1/memory").json() == []

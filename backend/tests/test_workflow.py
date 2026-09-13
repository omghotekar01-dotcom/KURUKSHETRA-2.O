from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.repositories.incidents import IncidentStore


def _client(tmp_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "workflow.db"))
    return TestClient(main_module.app)


def _remediation_ready_incident(client: TestClient) -> tuple[str, dict]:
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 after deployment",
            "description": "Successful login is followed by unauthorized API responses.",
            "logs": ["JWT signature verification failed"],
        },
    ).json()
    analysis = client.post(f"/api/v1/incidents/{created['id']}/analyze").json()
    return created["id"], analysis


def test_approved_bounded_action_moves_to_verification(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    client = _client(tmp_path, monkeypatch)
    incident_id, analysis = _remediation_ready_incident(client)

    response = client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
            "note": "Proceed in demo mode.",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["incident_status"] == "VERIFYING"
    assert result["execution"]["status"] == "SIMULATED"
    assert result["execution"]["mode"] == "DEMO"

    record = client.get(f"/api/v1/incidents/{incident_id}").json()
    assert record["status"] == "VERIFYING"
    assert [event["stage"] for event in record["timeline"]][-2:] == ["APPROVAL", "ACTION"]


def test_high_risk_action_is_blocked_even_after_approval(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    incident_id, _ = _remediation_ready_incident(client)

    response = client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "APPROVE",
            "action": {
                "action_type": "deploy",
                "target": "production",
                "description": "Deploy directly to production and restart production service",
                "confidence": 0.99,
                "destructive": False,
            },
            "reviewer": "Om",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["risk"]["risk"] == "HIGH"
    assert result["execution"] is None
    assert result["incident_status"] == "ESCALATED"

    record = client.get(f"/api/v1/incidents/{incident_id}").json()
    assert record["timeline"][-1]["stage"] == "ACTION_BLOCKED"


def test_verification_pass_resolves_incident(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    client = _client(tmp_path, monkeypatch)
    incident_id, analysis = _remediation_ready_incident(client)
    client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
        },
    )

    response = client.post(
        f"/api/v1/incidents/{incident_id}/verify",
        json={
            "outcome": "PASS",
            "evidence": "Authenticated reproduction request returned the expected success response.",
            "checked_by": "demo-verifier",
        },
    )

    assert response.status_code == 200
    assert response.json()["incident_status"] == "RESOLVED"

    record = client.get(f"/api/v1/incidents/{incident_id}").json()
    assert record["status"] == "RESOLVED"
    stages = [event["stage"] for event in record["timeline"]]
    assert "VERIFICATION" in stages
    assert stages[-1] == "MEMORY"

    memory = client.get("/api/v1/memory").json()
    assert any(item["incident_id"] == incident_id for item in memory)


def test_rejected_action_escalates_without_execution(tmp_path: Path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    incident_id, analysis = _remediation_ready_incident(client)

    response = client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "REJECT",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
            "note": "Need more evidence first.",
        },
    )

    assert response.status_code == 200
    assert response.json()["execution"] is None
    assert response.json()["incident_status"] == "ESCALATED"

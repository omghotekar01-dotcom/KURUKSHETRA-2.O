from pathlib import Path

import httpx
from fastapi.testclient import TestClient

import app.main as main_module
import app.services.execution as execution_module
from app.repositories.incidents import IncidentStore


def _client(tmp_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "github-action.db"))
    monkeypatch.setenv("GITHUB_REPOSITORY", "omghotekar01-dotcom/KURUKSHETRA-2.O")
    return TestClient(main_module.app)


def _ready_incident(client: TestClient) -> tuple[str, dict]:
    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "JWT failures after deployment",
            "description": "Authenticated users receive 401 responses after the latest release.",
            "environment": "production",
            "logs": ["JWT signature verification failed"],
        },
    ).json()
    analysis = client.post(f"/api/v1/incidents/{created['id']}/analyze").json()
    return created["id"], analysis


def test_approved_action_creates_real_github_issue_when_configured(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setattr(execution_module, "_github_token", lambda: "test-token")

    def fake_post(url, *, headers, json, timeout):
        assert url.endswith("/repos/omghotekar01-dotcom/KURUKSHETRA-2.O/issues")
        assert headers["Authorization"] == "Bearer test-token"
        assert "Evidence-backed RCA" in json["body"]
        assert timeout == 12.0
        request = httpx.Request("POST", url)
        return httpx.Response(
            201,
            json={"number": 42, "html_url": "https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O/issues/42"},
            request=request,
        )

    monkeypatch.setattr(execution_module.httpx, "post", fake_post)
    client = _client(tmp_path, monkeypatch)
    incident_id, analysis = _ready_incident(client)

    result = client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
        },
    )

    assert result.status_code == 200
    payload = result.json()
    assert payload["risk"]["risk"] == "MEDIUM"
    assert payload["risk"]["policy"] == "APPROVAL_REQUIRED"
    assert payload["execution"]["status"] == "EXECUTED"
    assert payload["execution"]["mode"] == "GITHUB"
    assert payload["execution"]["external_url"].endswith("/issues/42")
    assert payload["incident_status"] == "VERIFYING"


def test_live_github_action_fails_closed_without_auth(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setattr(execution_module, "_github_token", lambda: None)
    client = _client(tmp_path, monkeypatch)
    incident_id, analysis = _ready_incident(client)

    result = client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "APPROVE",
            "action": analysis["remediation"]["proposed_action"],
            "reviewer": "Om",
        },
    )

    assert result.status_code == 200
    payload = result.json()
    assert payload["execution"]["status"] == "PREPARED"
    assert payload["execution"]["mode"] == "SAFE_PREVIEW"
    assert payload["incident_status"] == "ESCALATED"

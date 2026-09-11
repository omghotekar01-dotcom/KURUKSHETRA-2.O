from fastapi.testclient import TestClient

import app.main as main_module


def test_readiness_reports_safety_without_exposing_token(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("INCIDENT_DB_PATH", "data/incidents.db")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_abcdefghijklmnopqrstuvwxyz123456")
    monkeypatch.setenv("ALLOW_GH_CLI_AUTH", "true")

    client = TestClient(main_module.app)
    response = client.get("/api/v1/evaluation/readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "READY"
    assert payload["mode"] == "LIVE_FIRST"
    assert payload["github"]["token_present"] is True
    assert payload["github"]["access_mode"] == "TOKEN_CONFIGURED"
    assert payload["safety"]["repository_evidence"] == "UNTRUSTED_DATA_ONLY"
    assert payload["safety"]["repository_writes"] == "EXPLICIT_HUMAN_APPROVAL_REQUIRED"
    assert payload["safety"]["automatic_merge"] is False
    assert "ghp_" not in response.text


def test_readiness_marks_demo_mode_degraded(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("INCIDENT_DB_PATH", "data/incidents.db")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "owner/repo")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    client = TestClient(main_module.app)
    payload = client.get("/api/v1/evaluation/readiness").json()

    assert payload["status"] == "DEGRADED"
    assert payload["mode"] == "FALLBACK_DEMO"
    assert payload["checks"]["live_mode_default"] is False

from fastapi.testclient import TestClient

from app.main import app
from app.routers import evaluation as evaluation_router
from app.schemas.workspace import ModelProbeResult, ModelRuntimeStatus


client = TestClient(app)


def test_default_readiness_does_not_perform_active_integration_probe(monkeypatch) -> None:
    def unexpected_write_probe(*args, **kwargs):
        raise AssertionError("default readiness must remain a fast non-network status call")

    monkeypatch.setattr(evaluation_router, "github_write_readiness", unexpected_write_probe)
    response = client.get("/api/v1/evaluation/readiness")
    assert response.status_code == 200
    payload = response.json()
    assert payload["github"]["write_probe"]["status"] == "NOT_PROBED"
    assert payload["model"]["mode"] == "NOT_PROBED"
    assert payload["safety"]["automatic_merge"] is False
    assert payload["safety"]["automatic_production_deploy"] is False


def test_active_readiness_surfaces_qwen_and_github_permission_without_secret(monkeypatch) -> None:
    monkeypatch.setattr(
        evaluation_router,
        "github_write_readiness",
        lambda repository: {
            "repository": repository,
            "authenticated": True,
            "auth_source": "GH_CLI",
            "write_access": True,
            "status": "READY",
            "reason": "push permission confirmed",
        },
    )
    monkeypatch.setattr(
        evaluation_router,
        "get_model_runtime_status",
        lambda: ModelRuntimeStatus(
            mode="LOCAL_OLLAMA",
            provider="ollama-local",
            model="qwen3:4b",
            ready=True,
            endpoint="http://localhost:11434/v1",
            note="installed",
        ),
    )
    monkeypatch.setattr(
        evaluation_router,
        "probe_model_runtime",
        lambda: ModelProbeResult(
            connected=True,
            provider="ollama-local",
            model="qwen3:4b",
            latency_ms=19,
            reply="READY",
            note="live inference succeeded",
        ),
    )

    response = client.get("/api/v1/evaluation/readiness?probe_integrations=true")
    assert response.status_code == 200
    payload = response.json()
    assert payload["github"]["write_probe"]["write_access"] is True
    assert payload["github"]["write_probe"]["auth_source"] == "GH_CLI"
    assert payload["model"]["connected"] is True
    assert payload["model"]["model"] == "qwen3:4b"
    assert payload["model"]["latency_ms"] == 19
    serialized = str(payload).lower()
    assert "authorization" not in serialized
    assert "bearer " not in serialized

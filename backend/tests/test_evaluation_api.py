from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_evaluation_api_returns_measured_report():
    response = client.get("/api/v1/evaluation/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["benchmark_version"] == "2026.09.12-v2"
    assert payload["deterministic"] is True
    assert len(payload["metrics"]) == 8
    assert len(payload["cases"]) == 21
    assert any(metric["key"] == "validation_success_rate" for metric in payload["metrics"])
    assert 0 <= payload["overall_score"] <= 1

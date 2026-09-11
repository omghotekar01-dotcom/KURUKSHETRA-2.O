from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_evaluation_api_returns_measured_report():
    response = client.get("/api/v1/evaluation/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["benchmark_version"] == "2026.09.11-v1"
    assert payload["deterministic"] is True
    assert len(payload["metrics"]) == 7
    assert len(payload["cases"]) == 20
    assert 0 <= payload["overall_score"] <= 1

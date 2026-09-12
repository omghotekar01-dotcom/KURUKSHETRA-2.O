from fastapi.testclient import TestClient

from app.main import app
from app.services.demo import get_demo_scenario, list_demo_scenarios


client = TestClient(app)


def test_demo_fixture_catalog_is_stable() -> None:
    scenarios = list_demo_scenarios()
    assert [item.id for item in scenarios] == [
        "DEMO-AUTH-001",
        "DEMO-DB-001",
        "DEMO-FRONTEND-001",
        "DEMO-INFRA-001",
        "DEMO-NOVEL-001",
    ]
    assert get_demo_scenario("demo-auth-001") is not None
    assert get_demo_scenario("missing") is None


def test_demo_scenarios_api_lists_local_fixtures() -> None:
    response = client.get("/api/v1/demo/scenarios")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert payload[0]["incident"]["environment"] == "production"
    assert {item["expected_component"] for item in payload} >= {"Authentication", "Database", "Frontend", "Infrastructure", "Unclassified"}


def test_demo_incident_endpoint_creates_auditable_case() -> None:
    response = client.post("/api/v1/demo/scenarios/DEMO-AUTH-001/incidents")
    assert response.status_code == 201
    payload = response.json()
    assert payload["triage"]["component"] == "Authentication"
    assert any(event["stage"] == "DEMO" for event in payload["timeline"])


def test_unknown_demo_scenario_returns_404() -> None:
    response = client.post("/api/v1/demo/scenarios/not-real/incidents")
    assert response.status_code == 404

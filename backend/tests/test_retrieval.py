from pathlib import Path

from app.repositories.incidents import IncidentStore
from app.schemas.incident import IncidentIn
from app.services.retrieval import retrieve_runbooks
from app.services.triage import triage_incident


def test_auth_incident_retrieves_jwt_runbook(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    payload = IncidentIn(
        title="401 after deployment",
        description="Users login successfully but every API call returns unauthorized.",
        logs=["JWT signature verification failed"],
    )
    record = store.create(payload, triage_incident(payload))

    matches = retrieve_runbooks(record)

    assert matches
    assert matches[0].id == "RB-AUTH-001"
    assert matches[0].score >= 0.18


def test_unrelated_incident_can_return_no_strong_match(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    payload = IncidentIn(
        title="Printer makes clicking sound",
        description="A physical office printer clicks when loading paper.",
        environment="office",
    )
    record = store.create(payload, triage_incident(payload))

    matches = retrieve_runbooks(record)

    assert matches == []

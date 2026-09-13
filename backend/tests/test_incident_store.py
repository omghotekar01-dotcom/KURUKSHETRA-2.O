from pathlib import Path

from app.repositories.incidents import IncidentStore
from app.schemas.incident import IncidentIn, IncidentStatus, Severity
from app.services.triage import triage_incident


def test_incident_store_persists_record_and_timeline(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    payload = IncidentIn(
        title="401 after deployment",
        description="Production users receive 401 responses immediately after login.",
        logs=["JWT signature verification failed"],
    )

    created = store.create(payload, triage_incident(payload))
    loaded = store.get(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.status is IncidentStatus.investigating
    assert loaded.triage.component == "Authentication"
    assert loaded.triage.severity is Severity.high
    assert [event.stage for event in loaded.timeline] == ["INTAKE", "TRIAGE"]


def test_incident_store_lists_newest_incidents(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    first = IncidentIn(title="Frontend button broken", description="Button overlaps text on mobile")
    second = IncidentIn(title="Database timeout", description="Postgres query timeout in production")

    store.create(first, triage_incident(first))
    store.create(second, triage_incident(second))

    items = store.list(limit=10)

    assert len(items) == 2
    assert {item.title for item in items} == {first.title, second.title}

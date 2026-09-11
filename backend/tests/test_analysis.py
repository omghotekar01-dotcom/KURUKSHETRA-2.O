from pathlib import Path

from app.repositories.incidents import IncidentStore
from app.schemas.incident import IncidentIn
from app.services.analysis import analyze_incident
from app.services.triage import triage_incident


def test_analysis_builds_evidence_hypothesis_and_remediation(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    payload = IncidentIn(
        title="401 after deployment",
        description="Users authenticate then protected API calls return unauthorized.",
        logs=["JWT signature verification failed"],
    )
    record = store.create(payload, triage_incident(payload))

    result = analyze_incident(record)

    assert result.needs_human_investigation is False
    assert result.hypotheses
    assert result.hypotheses[0].evidence_ids[0] == "RB-AUTH-001"
    assert result.remediation is not None
    assert "JWT" in result.remediation.summary
    assert result.remediation.verification


def test_analysis_escalates_when_retrieval_has_no_match(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    payload = IncidentIn(
        title="Printer makes clicking sound",
        description="A physical office printer clicks while loading paper.",
        environment="office",
    )
    record = store.create(payload, triage_incident(payload))

    result = analyze_incident(record)

    assert result.needs_human_investigation is True
    assert result.hypotheses == []
    assert result.remediation is None

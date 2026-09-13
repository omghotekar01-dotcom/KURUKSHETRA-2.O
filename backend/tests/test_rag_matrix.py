from __future__ import annotations

from pathlib import Path

import pytest

from app.repositories.incidents import IncidentStore
from app.schemas.incident import IncidentIn
from app.services.analysis import analyze_incident
from app.services.retrieval import retrieve_knowledge
from app.services.triage import triage_incident


CASES = [
    (
        "Authentication",
        "RB-AUTH-001",
        IncidentIn(
            title="401 after login",
            description="Protected API requests return unauthorized after a deployment.",
            logs=["JWT signature verification failed"],
        ),
    ),
    (
        "Database",
        "RB-DB-001",
        IncidentIn(
            title="Profile writes time out",
            description="Postgres requests fail while the connection pool is saturated.",
            logs=["postgres connection pool exhausted"],
        ),
    ),
    (
        "Backend",
        "RB-BE-001",
        IncidentIn(
            title="API returns 502",
            description="Reverse proxy cannot reach application workers.",
            logs=["nginx upstream connection refused to backend worker"],
        ),
    ),
    (
        "Frontend",
        "RB-FE-001",
        IncidentIn(
            title="Buttons overlap on mobile",
            description="A CSS change causes text and buttons to overlap at phone width.",
            logs=["frontend css responsive layout regression"],
        ),
    ),
    (
        "Infrastructure",
        "RB-INFRA-001",
        IncidentIn(
            title="Kubernetes pods keep restarting",
            description="Pods enter CrashLoopBackOff and readiness probes fail after rollout.",
            logs=["readiness probe failed kubernetes pod"],
        ),
    ),
]


@pytest.mark.parametrize(("component", "runbook_id", "incident"), CASES)
def test_rag_retrieves_expected_evidence_and_grounds_rca(
    tmp_path: Path,
    component: str,
    runbook_id: str,
    incident: IncidentIn,
) -> None:
    store = IncidentStore(tmp_path / f"{component.lower()}.db")
    record = store.create(incident, triage_incident(incident))

    assert record.triage.component == component

    matches = retrieve_knowledge(record, memories=[])
    assert matches
    assert runbook_id in [match.id for match in matches]
    assert matches[0].score >= 0.18

    analysis = analyze_incident(record, memories=[], repository_context=None)
    assert analysis.hypotheses
    assert runbook_id in analysis.hypotheses[0].evidence_ids
    assert analysis.needs_human_investigation is False


def test_rag_unknown_case_fails_closed_without_inventing_rca(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "unknown.db")
    incident = IncidentIn(
        title="Printer clicks while loading paper",
        description="A physical office printer makes a clicking sound when paper is inserted.",
        environment="office",
    )
    record = store.create(incident, triage_incident(incident))

    assert retrieve_knowledge(record, memories=[]) == []

    analysis = analyze_incident(record, memories=[], repository_context=None)
    assert analysis.hypotheses == []
    assert analysis.remediation is None
    assert analysis.needs_human_investigation is True
    assert analysis.evidence.no_strong_match is True

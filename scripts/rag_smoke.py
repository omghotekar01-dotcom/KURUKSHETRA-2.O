from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.repositories.incidents import IncidentStore  # noqa: E402
from app.schemas.incident import IncidentIn  # noqa: E402
from app.services.analysis import analyze_incident  # noqa: E402
from app.services.retrieval import DEFAULT_CORPUS, retrieve_knowledge  # noqa: E402
from app.services.triage import triage_incident  # noqa: E402


CASES = [
    (
        "Authentication",
        "RB-AUTH-001",
        IncidentIn(
            title="401 errors after login",
            description="Users authenticate successfully but protected API requests return unauthorized after deployment.",
            environment="production",
            logs=["JWT signature verification failed"],
        ),
    ),
    (
        "Database",
        "RB-DB-001",
        IncidentIn(
            title="Profile writes time out",
            description="Profile writes fail while PostgreSQL connections are saturated.",
            environment="production",
            logs=["postgres connection pool exhausted"],
        ),
    ),
    (
        "Backend",
        "RB-BE-001",
        IncidentIn(
            title="API returns 502",
            description="The reverse proxy cannot reach application workers after rollout.",
            environment="production",
            logs=["nginx upstream connection refused to backend worker"],
        ),
    ),
    (
        "Frontend",
        "RB-FE-001",
        IncidentIn(
            title="Buttons overlap on mobile",
            description="A CSS change causes buttons and text to overlap at phone width.",
            environment="production",
            logs=["frontend css responsive layout regression"],
        ),
    ),
    (
        "Infrastructure",
        "RB-INFRA-001",
        IncidentIn(
            title="Kubernetes pods keep restarting",
            description="Pods enter CrashLoopBackOff and readiness never becomes healthy after deployment.",
            environment="production",
            logs=["readiness probe failed kubernetes pod"],
        ),
    ),
]

NO_MATCH = IncidentIn(
    title="Printer clicks while loading paper",
    description="A physical office printer makes a clicking sound when paper is inserted.",
    environment="office",
    logs=[],
)


def _validate_corpus() -> None:
    entries = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8"))
    required = {"id", "component", "issue", "fix", "source"}
    ids: list[str] = []
    for entry in entries:
        missing = required - set(entry)
        if missing:
            raise AssertionError(f"runbook {entry.get('id', '<unknown>')} missing fields: {sorted(missing)}")
        if not all(str(entry[key]).strip() for key in required):
            raise AssertionError(f"runbook {entry['id']} contains an empty required field")
        ids.append(str(entry["id"]))
    if len(ids) != len(set(ids)):
        raise AssertionError("runbook IDs must be unique")
    print(f"[PASS] corpus schema: {len(entries)} runbooks, unique IDs, required fields present")


def main() -> int:
    _validate_corpus()
    # sqlite3 connections can release their Windows file handle a moment after the
    # final operation. Cleanup is best-effort because this smoke test validates RAG,
    # not temporary-directory deletion semantics.
    with tempfile.TemporaryDirectory(prefix="bug-router-rag-smoke-", ignore_cleanup_errors=True) as temp_dir:
        store = IncidentStore(Path(temp_dir) / "incidents.db")

        for expected_component, expected_runbook, incident in CASES:
            record = store.create(incident, triage_incident(incident))
            if record.triage.component != expected_component:
                raise AssertionError(
                    f"routing mismatch for {expected_runbook}: expected {expected_component}, got {record.triage.component}"
                )

            matches = retrieve_knowledge(record, memories=[])
            ids = [match.id for match in matches]
            if expected_runbook not in ids:
                raise AssertionError(f"RAG miss for {expected_runbook}: retrieved {ids or ['<none>']}")

            top = matches[0]
            analysis = analyze_incident(record, memories=[], repository_context=None)
            if not analysis.hypotheses or expected_runbook not in analysis.hypotheses[0].evidence_ids:
                evidence_ids = analysis.hypotheses[0].evidence_ids if analysis.hypotheses else []
                raise AssertionError(f"RCA is not grounded in {expected_runbook}: {evidence_ids}")

            print(
                f"[PASS] {expected_component}: expected {expected_runbook}, "
                f"top={top.id}, score={top.score:.3f}, RCA grounded"
            )

        record = store.create(NO_MATCH, triage_incident(NO_MATCH))
        matches = retrieve_knowledge(record, memories=[])
        analysis = analyze_incident(record, memories=[], repository_context=None)
        if matches:
            raise AssertionError(f"no-match case unexpectedly retrieved {[match.id for match in matches]}")
        if not analysis.needs_human_investigation or analysis.hypotheses:
            raise AssertionError("no-match case must fail closed and require human investigation")
        print("[PASS] no-match: no evidence invented; human investigation required")

    print("RAG + RCA SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

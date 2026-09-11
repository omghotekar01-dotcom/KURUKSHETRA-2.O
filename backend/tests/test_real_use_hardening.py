from datetime import datetime, timezone

import pytest

from app.schemas.incident import (
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    PatchProposalRequest,
    RepositoryCommitEvidence,
    RepositoryContext,
    RepositoryDiffHunkEvidence,
    RepositoryFileChange,
    RepositorySourceLine,
    Severity,
    TriageResult,
)
from app.services import patch_execution
from app.services.github_context import _incident_path_hints, _parse_patch_hunks
from app.services.patch_proposal import PatchProposalUnavailable, build_patch_proposal
from app.services.triage import triage_incident


@pytest.mark.parametrize(
    ("incident", "expected_component"),
    [
        (
            IncidentIn(
                title="Refresh token rejected for signed-in users",
                description="Protected endpoints return unauthorized immediately after login.",
                logs=["JWT signature verification failed while validating bearer token"],
            ),
            "Authentication",
        ),
        (
            IncidentIn(
                title="Checkout requests hang waiting for storage",
                description="Database-backed requests are timing out under normal load.",
                logs=["postgres connection pool exhausted; waiting for available connection"],
            ),
            "Database",
        ),
        (
            IncidentIn(
                title="502 from API gateway after release",
                description="The public API is returning upstream failures.",
                logs=["uvicorn worker unavailable; upstream returned 502"],
            ),
            "Backend",
        ),
        (
            IncidentIn(
                title="Checkout modal overlaps submit button on mobile",
                description="The browser UI regressed on narrow viewports.",
                logs=["React modal CSS overflow on 390px viewport"],
            ),
            "Frontend",
        ),
        (
            IncidentIn(
                title="Pods restart repeatedly after rollout",
                description="The workload never becomes healthy.",
                logs=["Kubernetes pod CrashLoopBackOff after OOM memory pressure"],
            ),
            "Infrastructure",
        ),
    ],
)
def test_realistic_incidents_route_to_expected_component(incident: IncidentIn, expected_component: str) -> None:
    result = triage_incident(incident)
    assert result.component == expected_component
    assert result.owner_team
    assert result.confidence >= 0.55


def _stacktrace_record() -> IncidentRecord:
    now = datetime.now(timezone.utc)
    incident = IncidentIn(
        title="500 while charging a card",
        description=(
            "Checkout started failing after the latest release. Traceback points to "
            "backend/payments/charge.py:87 while building the provider request."
        ),
        environment="production",
        repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
        logs=[
            'File "C:\\service\\backend\\payments\\charge.py", line 87, in create_charge',
            "ValueError: invalid provider amount",
        ],
    )
    return IncidentRecord(
        id="INC-REAL-001",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.investigating,
        incident=incident,
        triage=triage_incident(incident),
        timeline=[],
    )


def test_stacktrace_file_path_is_a_strong_repository_ranking_signal() -> None:
    record = _stacktrace_record()
    hints = _incident_path_hints(record)
    assert any(hint.endswith("backend/payments/charge.py") for hint in hints)

    matching = _parse_patch_hunks(
        record,
        "backend/payments/charge.py",
        "@@ -84,6 +84,7 @@ def create_charge(amount):\n+    provider_amount = str(amount)\n",
    )[0]
    unrelated = _parse_patch_hunks(
        record,
        "docs/architecture.md",
        "@@ -4,3 +4,4 @@ Overview\n+Updated component diagram\n",
    )[0]

    assert matching.correlation_score >= 0.6
    assert matching.correlation_score > unrelated.correlation_score
    assert "backend/payments/charge.py" in matching.matched_terms


def _weak_patch_context(record: IncidentRecord) -> RepositoryContext:
    hunk = RepositoryDiffHunkEvidence(
        filename="frontend/src/banner.tsx",
        header="@@ -1,2 +1,3 @@",
        added_lines=["const banner = 'hello'"],
        removed_lines=[],
        matched_terms=[],
        source_context=[
            RepositorySourceLine(line_number=1, content="const banner = 'hello'", in_hunk=True),
        ],
        correlation_score=0.05,
    )
    return RepositoryContext(
        repository=record.incident.repo or "",
        default_branch="main",
        fetched_at=datetime.now(timezone.utc),
        authenticated=False,
        source="github-live",
        commits=[
            RepositoryCommitEvidence(
                sha="abcdef1234567890abcdef1234567890abcdef12",
                short_sha="abcdef1",
                message="chore: change banner copy",
                author="Engineer",
                authored_at=datetime.now(timezone.utc),
                url="https://github.com/example/repo/commit/abcdef1",
                files=[
                    RepositoryFileChange(
                        filename=hunk.filename,
                        status="modified",
                        additions=1,
                        deletions=0,
                        changes=1,
                    )
                ],
                suspicious_hunks=[hunk],
                correlation_score=0.05,
            )
        ],
        open_issues=[],
        notes=[],
    )


def test_patch_proposal_refuses_weakly_related_code_even_if_exact_lines_exist() -> None:
    record = _stacktrace_record()
    context = _weak_patch_context(record)
    request = PatchProposalRequest(
        commit_sha=context.commits[0].sha,
        filename=context.commits[0].suspicious_hunks[0].filename,
        hunk_header=context.commits[0].suspicious_hunks[0].header,
    )

    with pytest.raises(PatchProposalUnavailable, match="safety threshold"):
        build_patch_proposal(record, context, request)


def test_validation_gate_is_reproducible_and_fails_closed_for_unsupported_operational_files() -> None:
    frontend = patch_execution._validation_plan("frontend/src/App.tsx")
    assert frontend is not None
    assert frontend[0][2][1] == "ci"

    assert patch_execution._validation_plan("README.md") == []
    assert patch_execution._validation_plan(".github/workflows/deploy.yml") is None
    assert patch_execution._validation_plan("Dockerfile") is None
    assert patch_execution._validation_plan("infra/main.tf") is None
    assert patch_execution._validation_plan("config/custom.runtime") is None

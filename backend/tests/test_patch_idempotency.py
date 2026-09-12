from datetime import datetime, timezone

from app.routers.patches import _existing_successful_execution
from app.schemas.incident import (
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    PatchProposal,
    Severity,
    TimelineEvent,
    TriageResult,
)
from app.services.patch_execution import _branch_name, _find_existing_pr, patch_idempotency_key


def _proposal(after: str = "const broken = false") -> PatchProposal:
    return PatchProposal(
        proposal_id="PATCH-ABC123",
        incident_id="INC-TEST123",
        repository="omghotekar01-dotcom/KURUKSHETRA-2.O",
        base_commit="abcdef1234567890",
        file_path="frontend/src/example.ts",
        hunk_header="@@ -1,1 +1,1 @@",
        line_start=1,
        before_lines=["const broken = true"],
        after_lines=[after],
        diff_preview=f"-const broken = true\n+{after}",
        rationale="Bounded test proposal",
        confidence=0.7,
        verification_commands=["cd frontend && npm run build"],
        warnings=[],
        writes_repository=False,
    )


def _incident(timeline: list[TimelineEvent] | None = None) -> IncidentRecord:
    now = datetime.now(timezone.utc)
    return IncidentRecord(
        id="INC-TEST123",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.verifying,
        incident=IncidentIn(
            title="Frontend build regression",
            description="Build fails after a recent change.",
            environment="development",
            repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
            logs=["typescript build failed"],
        ),
        triage=TriageResult(
            component="Frontend",
            owner_team="frontend-team",
            severity=Severity.medium,
            confidence=0.8,
            summary="Frontend build regression",
            signals=["frontend"],
        ),
        timeline=timeline or [],
    )


def test_idempotency_key_is_stable_for_exact_proposal() -> None:
    first = patch_idempotency_key("INC-TEST123", _proposal())
    second = patch_idempotency_key("INC-TEST123", _proposal())
    changed = patch_idempotency_key("INC-TEST123", _proposal("const broken = maybe"))
    assert first == second
    assert first.startswith("REM-")
    assert first != changed


def test_fix_branch_name_is_deterministic() -> None:
    first = _branch_name("INC-TEST123", "PATCH-ABC123")
    second = _branch_name("INC-TEST123", "PATCH-ABC123")
    assert first == second == "incident-fix/inc-test123-patch-abc123"


def test_existing_pr_lookup_reuses_matching_branch() -> None:
    payload = [
        {"number": 8, "head": {"ref": "other-branch"}},
        {"number": 9, "head": {"ref": "incident-fix/inc-test123-patch-abc123"}, "state": "open"},
    ]
    match = _find_existing_pr(payload, "incident-fix/inc-test123-patch-abc123")
    assert match is not None
    assert match["number"] == 9


def test_completed_execution_can_be_reconstructed_without_second_write() -> None:
    proposal = _proposal()
    key = patch_idempotency_key("INC-TEST123", proposal)
    event = TimelineEvent(
        timestamp=datetime.now(timezone.utc),
        stage="PATCH_EXECUTION",
        message="Draft PR created",
        metadata={
            "proposal_id": proposal.proposal_id,
            "status": "DRAFT_PR_CREATED",
            "repository": proposal.repository,
            "branch": "incident-fix/inc-test123-patch-abc123",
            "branch_url": "https://github.com/example/repo/tree/fix",
            "commit_sha": "1234567890abcdef",
            "draft_pr_number": 42,
            "draft_pr_url": "https://github.com/example/repo/pull/42",
            "validation": [
                {
                    "name": "approved patch integrity",
                    "command": "re-read exact file",
                    "status": "PASS",
                    "exit_code": None,
                    "output": "ok",
                }
            ],
            "idempotency_key": key,
        },
    )
    result = _existing_successful_execution(_incident([event]), proposal.proposal_id, key)
    assert result is not None
    assert result.reused is True
    assert result.status == "DRAFT_PR_CREATED"
    assert result.draft_pr_number == 42
    assert result.idempotency_key == key

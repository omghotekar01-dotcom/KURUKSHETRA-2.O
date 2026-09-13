from datetime import datetime, timezone

import pytest

from app.schemas.incident import IncidentIn, IncidentRecord, IncidentStatus, PatchProposal, Severity, TriageResult
from app.services import patch_execution


def _incident() -> IncidentRecord:
    now = datetime.now(timezone.utc)
    return IncidentRecord(
        id="INC-TEST123",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.remediation_ready,
        incident=IncidentIn(
            title="Frontend build regression",
            description="Build fails after a recent change.",
            environment="development",
            repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
            logs=["typescript build failed"],
        ),
        triage=TriageResult(
            component="Frontend",
            owner_team="Frontend",
            severity=Severity.medium,
            confidence=0.8,
            summary="Frontend build regression",
            signals=["frontend"],
        ),
        timeline=[],
    )


def _proposal() -> PatchProposal:
    return PatchProposal(
        proposal_id="PATCH-ABC123",
        incident_id="INC-TEST123",
        repository="omghotekar01-dotcom/KURUKSHETRA-2.O",
        base_commit="abcdef1234567890",
        file_path="frontend/src/example.ts",
        hunk_header="@@ -1,1 +1,1 @@",
        line_start=1,
        before_lines=["const broken = true"],
        after_lines=["const broken = false"],
        diff_preview="-const broken = true\n+const broken = false",
        rationale="Bounded test proposal",
        confidence=0.7,
        verification_commands=["cd frontend && npm run build"],
        warnings=[],
        writes_repository=False,
    )


def test_replace_exact_sequence_changes_only_one_match() -> None:
    source = "alpha\nconst broken = true\nomega\n"
    result = patch_execution._replace_exact_sequence(source, ["const broken = true"], ["const broken = false"])
    assert result == "alpha\nconst broken = false\nomega\n"


def test_replace_exact_sequence_rejects_ambiguous_match() -> None:
    source = "same\nother\nsame\n"
    with pytest.raises(patch_execution.PatchExecutionError, match="more than once"):
        patch_execution._replace_exact_sequence(source, ["same"], ["new"])


def test_validation_plan_routes_frontend_and_backend() -> None:
    frontend = patch_execution._validation_plan("frontend/src/App.tsx")
    backend = patch_execution._validation_plan("backend/app/main.py")
    docs = patch_execution._validation_plan("README.md")
    assert frontend and frontend[-1][0] == "frontend production build"
    assert backend and backend[-1][0] == "backend tests"
    assert docs == []


def test_execution_fails_closed_without_live_credentials(monkeypatch) -> None:
    monkeypatch.setattr(patch_execution, "repository_allowed", lambda repository: True)
    monkeypatch.setattr(patch_execution, "github_token", lambda: None)
    result = patch_execution.execute_approved_patch(_incident(), _proposal())
    assert result.status == "AUTH_REQUIRED"
    assert result.branch is None
    assert result.draft_pr_url is None

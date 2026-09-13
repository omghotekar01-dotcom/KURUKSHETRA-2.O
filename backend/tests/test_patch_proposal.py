from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.repositories.incidents import IncidentStore
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
from app.services.patch_proposal import PatchProposalUnavailable, build_patch_proposal


def _incident() -> IncidentRecord:
    now = datetime.now(timezone.utc)
    return IncidentRecord(
        id="INC-PATCH-001",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.remediation_ready,
        incident=IncidentIn(
            title="Frontend build fails after unsupported icon import",
            description="TypeScript reports that lucide-react does not export the selected icon.",
            environment="development",
            repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
            logs=['TS2305: Module "lucide-react" has no exported member "Github"'],
        ),
        triage=TriageResult(
            component="Frontend",
            owner_team="Web Experience",
            severity=Severity.medium,
            confidence=0.88,
            summary="Frontend compile regression",
            signals=["typescript", "lucide", "github"],
        ),
        timeline=[],
    )


def _context() -> RepositoryContext:
    hunk = RepositoryDiffHunkEvidence(
        filename="frontend/src/App.tsx",
        header="@@ -6,6 +6,7 @@ import {",
        added_lines=["  Github,"],
        removed_lines=["  GitBranch,"],
        matched_terms=["github", "frontend"],
        source_context=[
            RepositorySourceLine(line_number=5, content="  ExternalLink,", in_hunk=False),
            RepositorySourceLine(line_number=6, content="  Github,", in_hunk=True),
            RepositorySourceLine(line_number=7, content="  History,", in_hunk=False),
        ],
        correlation_score=0.78,
    )
    return RepositoryContext(
        repository="omghotekar01-dotcom/KURUKSHETRA-2.O",
        default_branch="main",
        fetched_at=datetime.now(timezone.utc),
        authenticated=False,
        source="github-live",
        commits=[
            RepositoryCommitEvidence(
                sha="abcdef1234567890abcdef1234567890abcdef12",
                short_sha="abcdef1",
                message="feat: add repository evidence icon",
                author="Engineer",
                authored_at=datetime.now(timezone.utc),
                url="https://github.com/example/repo/commit/abcdef1",
                files=[
                    RepositoryFileChange(
                        filename="frontend/src/App.tsx",
                        status="modified",
                        additions=1,
                        deletions=1,
                        changes=2,
                    )
                ],
                suspicious_hunks=[hunk],
                correlation_score=0.74,
            )
        ],
        open_issues=[],
        notes=[],
    )


def test_build_patch_proposal_is_exact_and_read_only() -> None:
    request = PatchProposalRequest(
        commit_sha="abcdef1234567890abcdef1234567890abcdef12",
        filename="frontend/src/App.tsx",
        hunk_header="@@ -6,6 +6,7 @@ import {",
    )
    proposal = build_patch_proposal(_incident(), _context(), request)

    assert proposal.writes_repository is False
    assert proposal.strategy == "REVERT_SUSPICIOUS_HUNK"
    assert proposal.line_start == 6
    assert proposal.before_lines == ["  Github,"]
    assert proposal.after_lines == ["  GitBranch,"]
    assert "npm run build" in proposal.verification_commands[0]
    assert "-  Github," in proposal.diff_preview
    assert "+  GitBranch," in proposal.diff_preview


def test_build_patch_proposal_rejects_stale_source_context() -> None:
    context = _context()
    context.commits[0].suspicious_hunks[0].source_context[1].content = "  GitBranch,"
    request = PatchProposalRequest(
        commit_sha=context.commits[0].sha,
        filename="frontend/src/App.tsx",
        hunk_header=context.commits[0].suspicious_hunks[0].header,
    )

    try:
        build_patch_proposal(_incident(), context, request)
    except PatchProposalUnavailable as exc:
        assert "no longer contains" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected stale source context to block the proposal")


def test_patch_proposal_api_records_audit_event(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "patch-proposal.db"))
    monkeypatch.setattr(main_module, "collect_repository_context", lambda incident: _context())
    client = TestClient(main_module.app)

    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "Frontend build fails after unsupported icon import",
            "description": "TypeScript reports that lucide-react does not export the selected icon.",
            "environment": "development",
            "repo": "omghotekar01-dotcom/KURUKSHETRA-2.O",
            "logs": ['TS2305: Module "lucide-react" has no exported member "Github"'],
        },
    ).json()

    response = client.post(
        f"/api/v1/incidents/{created['id']}/patch-proposal",
        json={
            "commit_sha": "abcdef1234567890abcdef1234567890abcdef12",
            "filename": "frontend/src/App.tsx",
            "hunk_header": "@@ -6,6 +6,7 @@ import {",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["writes_repository"] is False
    assert payload["file_path"] == "frontend/src/App.tsx"
    assert payload["before_lines"] == ["  Github,"]
    assert payload["after_lines"] == ["  GitBranch,"]

    record = client.get(f"/api/v1/incidents/{created['id']}").json()
    proposal_events = [event for event in record["timeline"] if event["stage"] == "PATCH_PROPOSAL"]
    assert len(proposal_events) == 1
    assert proposal_events[0]["metadata"]["writes_repository"] is False

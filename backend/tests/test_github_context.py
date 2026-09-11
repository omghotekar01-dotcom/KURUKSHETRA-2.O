from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
import app.services.github_context as github_context_module
from app.repositories.incidents import IncidentStore
from app.schemas.incident import (
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    RepositoryCommitEvidence,
    RepositoryContext,
    RepositoryFileChange,
    Severity,
    TriageResult,
)
from app.services.github_context import GitHubContextUnavailable, collect_repository_context


def _record() -> IncidentRecord:
    now = datetime.now(timezone.utc)
    return IncidentRecord(
        id="INC-REPO-001",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.investigating,
        incident=IncidentIn(
            title="JWT failures after auth middleware change",
            description="Authenticated users receive 401 responses after the latest release.",
            repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
            logs=["JWT signature verification failed"],
        ),
        triage=TriageResult(
            component="Authentication",
            owner_team="Identity Platform",
            severity=Severity.high,
            confidence=0.9,
            summary="Authentication regression",
            signals=["jwt", "401"],
        ),
        timeline=[],
    )


def test_collect_repository_context_uses_live_github_payloads(monkeypatch) -> None:
    record = _record()
    monkeypatch.setattr(github_context_module, "github_token", lambda: None)
    monkeypatch.setattr(github_context_module, "repository_allowed", lambda repo: True)

    def fake_request(client, path, *, params=None):
        if path == "/repos/omghotekar01-dotcom/KURUKSHETRA-2.O":
            return {"default_branch": "main"}
        if path.endswith("/commits"):
            return [{"sha": "abcdef1234567890"}, {"sha": "9999999999999999"}]
        if path.endswith("/commits/abcdef1234567890"):
            return {
                "sha": "abcdef1234567890",
                "html_url": "https://github.com/example/repo/commit/abcdef1",
                "commit": {
                    "message": "fix auth middleware jwt verification",
                    "author": {"name": "Engineer", "date": "2026-09-11T08:00:00Z"},
                },
                "files": [
                    {"filename": "backend/auth/jwt.py", "status": "modified", "additions": 8, "deletions": 2, "changes": 10}
                ],
            }
        if path.endswith("/commits/9999999999999999"):
            return {
                "sha": "9999999999999999",
                "html_url": "https://github.com/example/repo/commit/9999999",
                "commit": {
                    "message": "docs: update readme",
                    "author": {"name": "Engineer", "date": "2026-09-11T07:00:00Z"},
                },
                "files": [
                    {"filename": "README.md", "status": "modified", "additions": 2, "deletions": 0, "changes": 2}
                ],
            }
        if path.endswith("/issues"):
            return [
                {"number": 12, "title": "Auth regression", "state": "open", "html_url": "https://github.com/example/repo/issues/12", "labels": [{"name": "bug"}]},
                {"number": 13, "title": "A pull request", "state": "open", "html_url": "https://github.com/example/repo/pull/13", "labels": [], "pull_request": {}},
            ]
        raise AssertionError(path)

    monkeypatch.setattr(github_context_module, "_request_json", fake_request)
    context = collect_repository_context(record)

    assert context.source == "github-live"
    assert context.authenticated is False
    assert context.commits[0].short_sha == "abcdef1"
    assert context.commits[0].correlation_score > context.commits[1].correlation_score
    assert context.commits[0].files[0].filename == "backend/auth/jwt.py"
    assert len(context.open_issues) == 1
    assert context.open_issues[0].number == 12


def test_repository_context_rejects_unapproved_repository(monkeypatch) -> None:
    record = _record().model_copy(
        update={"incident": _record().incident.model_copy(update={"repo": "outside/repository"})}
    )
    monkeypatch.setattr(github_context_module, "repository_allowed", lambda repo: False)

    try:
        collect_repository_context(record)
    except GitHubContextUnavailable as exc:
        assert "allowlist" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected repository allowlist rejection")


def test_analyze_includes_repository_evidence_in_api_response(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main_module, "incident_store", IncidentStore(tmp_path / "repo-context.db"))
    context = RepositoryContext(
        repository="omghotekar01-dotcom/KURUKSHETRA-2.O",
        default_branch="main",
        fetched_at=datetime.now(timezone.utc),
        authenticated=False,
        source="github-live",
        commits=[
            RepositoryCommitEvidence(
                sha="abcdef1234567890",
                short_sha="abcdef1",
                message="fix auth middleware jwt verification",
                author="Engineer",
                authored_at=datetime.now(timezone.utc),
                url="https://github.com/example/repo/commit/abcdef1",
                correlation_score=0.75,
                files=[
                    RepositoryFileChange(
                        filename="backend/auth/jwt.py",
                        status="modified",
                        additions=8,
                        deletions=2,
                        changes=10,
                    )
                ],
            )
        ],
        open_issues=[],
        notes=[],
    )
    monkeypatch.setattr(main_module, "collect_repository_context", lambda incident: context)
    client = TestClient(main_module.app)

    created = client.post(
        "/api/v1/incidents",
        json={
            "title": "401 after auth middleware change",
            "description": "Authenticated users receive 401 responses after the latest release.",
            "repo": "omghotekar01-dotcom/KURUKSHETRA-2.O",
            "logs": ["JWT signature verification failed"],
        },
    ).json()
    response = client.post(f"/api/v1/incidents/{created['id']}/analyze")

    assert response.status_code == 200
    payload = response.json()
    assert payload["repository_context"]["source"] == "github-live"
    assert "GH-COMMIT-abcdef1" in payload["hypotheses"][0]["evidence_ids"]
    assert "Live GitHub evidence" in payload["hypotheses"][0]["rationale"]

    record = client.get(f"/api/v1/incidents/{created['id']}").json()
    stages = [event["stage"] for event in record["timeline"]]
    assert "REPOSITORY_EVIDENCE" in stages

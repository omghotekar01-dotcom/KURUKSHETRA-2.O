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
    RepositoryDiffHunkEvidence,
    RepositoryFileChange,
    RepositorySourceLine,
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
            signals=["jwt", "401", "signature"],
        ),
        timeline=[],
    )


def test_collect_repository_context_uses_live_github_payloads(monkeypatch) -> None:
    record = _record()
    monkeypatch.setattr(github_context_module, "github_token", lambda: None)
    monkeypatch.setattr(github_context_module, "repository_allowed", lambda repo: True)
    monkeypatch.setattr(github_context_module, "_fetch_codeowners", lambda client, repository, ref: None)
    monkeypatch.setattr(
        github_context_module,
        "_fetch_source_context",
        lambda client, repository, commit_sha, hunk: [
            RepositorySourceLine(line_number=41, content="verify_signature(token, jwt_signing_key)", in_hunk=True),
            RepositorySourceLine(line_number=42, content="validate_jwt_claims(token)", in_hunk=True),
        ],
    )

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
                    {
                        "filename": "backend/auth/jwt.py",
                        "status": "modified",
                        "additions": 8,
                        "deletions": 2,
                        "changes": 10,
                        "patch": "@@ -41,6 +41,8 @@ def verify_token(token):\n-    verify_signature(token, old_key)\n+    verify_signature(token, jwt_signing_key)\n+    validate_jwt_claims(token)\n",
                    }
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
                    {
                        "filename": "README.md",
                        "status": "modified",
                        "additions": 2,
                        "deletions": 0,
                        "changes": 2,
                        "patch": "@@ -1,2 +1,3 @@\n # Project\n+Documentation refresh\n",
                    }
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
    assert context.commits[0].suspicious_hunks
    assert context.commits[0].suspicious_hunks[0].filename == "backend/auth/jwt.py"
    assert "jwt" in context.commits[0].suspicious_hunks[0].matched_terms
    assert context.commits[0].suspicious_hunks[0].correlation_score > 0
    assert context.commits[0].suspicious_hunks[0].source_context[0].line_number == 41
    assert context.commits[0].suspicious_hunks[0].source_context[0].in_hunk is True
    assert len(context.open_issues) == 1
    assert context.open_issues[0].number == 12


def test_codeowners_uses_last_match_and_returns_real_repository_owners() -> None:
    rules = github_context_module._parse_codeowners(
        """
# broad fallback
* @engineering
/backend/ @backend-team
/backend/auth/* @identity-platform @security-reviewers
"""
    )
    owners = github_context_module._owners_for_files(
        rules,
        ["backend/auth/jwt.py", "backend/payments/charge.py", "README.md"],
    )

    assert owners == ["@identity-platform", "@security-reviewers", "@backend-team", "@engineering"]


def test_collect_repository_context_exposes_codeowner_hints(monkeypatch) -> None:
    record = _record()
    monkeypatch.setattr(github_context_module, "github_token", lambda: None)
    monkeypatch.setattr(github_context_module, "repository_allowed", lambda repo: True)
    monkeypatch.setattr(
        github_context_module,
        "_fetch_codeowners",
        lambda client, repository, ref: (
            ".github/CODEOWNERS",
            github_context_module._parse_codeowners("/backend/auth/* @identity-platform @security-reviewers"),
        ),
    )
    monkeypatch.setattr(
        github_context_module,
        "_fetch_source_context",
        lambda client, repository, commit_sha, hunk: [
            RepositorySourceLine(line_number=41, content="verify_signature(token, jwt_signing_key)", in_hunk=True),
        ],
    )

    def fake_request(client, path, *, params=None):
        if path == "/repos/omghotekar01-dotcom/KURUKSHETRA-2.O":
            return {"default_branch": "main"}
        if path.endswith("/commits"):
            return [{"sha": "abcdef1234567890"}]
        if path.endswith("/commits/abcdef1234567890"):
            return {
                "sha": "abcdef1234567890",
                "html_url": "https://github.com/example/repo/commit/abcdef1",
                "commit": {
                    "message": "fix jwt signature handling",
                    "author": {"name": "Engineer", "date": "2026-09-11T08:00:00Z"},
                },
                "files": [
                    {
                        "filename": "backend/auth/jwt.py",
                        "status": "modified",
                        "additions": 1,
                        "deletions": 1,
                        "changes": 2,
                        "patch": "@@ -41,1 +41,1 @@\n-verify_signature(token, old_key)\n+verify_signature(token, jwt_signing_key)\n",
                    }
                ],
            }
        if path.endswith("/issues"):
            return []
        raise AssertionError(path)

    monkeypatch.setattr(github_context_module, "_request_json", fake_request)
    context = collect_repository_context(record)

    assert context.suggested_owners == ["@identity-platform", "@security-reviewers"]
    assert context.ownership_source == ".github/CODEOWNERS"
    assert any("routing/review suggestions" in note for note in context.notes)


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
                suspicious_hunks=[
                    RepositoryDiffHunkEvidence(
                        filename="backend/auth/jwt.py",
                        header="@@ -41,6 +41,8 @@ def verify_token(token)",
                        added_lines=["verify_signature(token, jwt_signing_key)"],
                        removed_lines=["verify_signature(token, old_key)"],
                        matched_terms=["jwt", "signature"],
                        source_context=[
                            RepositorySourceLine(line_number=41, content="verify_signature(token, jwt_signing_key)", in_hunk=True)
                        ],
                        correlation_score=0.8,
                    )
                ],
            )
        ],
        open_issues=[],
        suggested_owners=["@identity-platform"],
        ownership_source=".github/CODEOWNERS",
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
    assert payload["repository_context"]["suggested_owners"] == ["@identity-platform"]
    assert payload["repository_context"]["commits"][0]["suspicious_hunks"][0]["source_context"][0]["line_number"] == 41
    assert "GH-COMMIT-abcdef1" in payload["hypotheses"][0]["evidence_ids"]
    assert any(item.startswith("GH-HUNK-abcdef1") for item in payload["hypotheses"][0]["evidence_ids"])
    assert "live diff hunk" in payload["hypotheses"][0]["rationale"].lower()

    record = client.get(f"/api/v1/incidents/{created['id']}").json()
    stages = [event["stage"] for event in record["timeline"]]
    assert "REPOSITORY_EVIDENCE" in stages

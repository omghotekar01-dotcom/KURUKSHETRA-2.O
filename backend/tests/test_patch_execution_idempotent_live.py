import base64
from datetime import datetime, timezone

from app.schemas.incident import IncidentIn, IncidentRecord, IncidentStatus, PatchProposal, Severity, TriageResult
from app.schemas.patch import ValidationCheck
from app.services import patch_execution


def _incident() -> IncidentRecord:
    now = datetime.now(timezone.utc)
    return IncidentRecord(
        id="INC-TEST123",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.remediation_ready,
        incident=IncidentIn(
            title="Frontend regression",
            description="A deterministic test incident.",
            environment="development",
            repo="omghotekar01-dotcom/KURUKSHETRA-2.O",
            logs=["frontend regression"],
        ),
        triage=TriageResult(
            component="Frontend",
            owner_team="frontend-team",
            severity=Severity.medium,
            confidence=0.8,
            summary="Frontend regression",
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
        file_path="README.md",
        hunk_header="@@ -1 +1 @@",
        line_start=1,
        before_lines=["broken"],
        after_lines=["fixed"],
        diff_preview="-broken\n+fixed",
        rationale="bounded test",
        confidence=0.8,
        verification_commands=["content integrity"],
        warnings=[],
        writes_repository=False,
    )


def _file(content: str, sha: str = "blob-sha") -> dict:
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha,
    }


def _patch_common(monkeypatch) -> None:
    monkeypatch.setattr(patch_execution, "repository_allowed", lambda repository: True)
    monkeypatch.setattr(patch_execution, "github_token", lambda: "token")
    monkeypatch.setattr(
        patch_execution,
        "_run_local_validation",
        lambda repository, branch, file_path: [
            ValidationCheck(name="non-code change gate", command="integrity", status="PASS", output="ok")
        ],
    )


def test_new_deterministic_branch_is_reread_then_written(monkeypatch) -> None:
    _patch_common(monkeypatch)
    state = {"branch_gets": 0, "written": False, "ref_posts": 0, "pr_posts": 0}

    def optional_get(client, path, params=None):
        state["branch_gets"] += 1
        if state["branch_gets"] == 1:
            return None
        return {"object": {"sha": "base-sha"}}

    def api(client, method, path, json=None, params=None):
        if method == "GET" and path.endswith("/repos/omghotekar01-dotcom/KURUKSHETRA-2.O"):
            return {"default_branch": "main"}
        if method == "GET" and "/git/ref/heads/main" in path:
            return {"object": {"sha": "base-sha"}}
        if method == "GET" and "/contents/README.md" in path:
            if params and params.get("ref", "").startswith("incident-fix/"):
                return _file("fixed\n" if state["written"] else "broken\n")
            return _file("broken\n")
        if method == "POST" and path.endswith("/git/refs"):
            state["ref_posts"] += 1
            return {}
        if method == "PUT" and "/contents/README.md" in path:
            state["written"] = True
            return {"commit": {"sha": "fix-commit"}}
        if method == "GET" and path.endswith("/pulls"):
            return []
        if method == "POST" and path.endswith("/pulls"):
            state["pr_posts"] += 1
            return {"number": 17, "html_url": "https://github.com/example/repo/pull/17"}
        raise AssertionError((method, path, params))

    monkeypatch.setattr(patch_execution, "_optional_get", optional_get)
    monkeypatch.setattr(patch_execution, "_api", api)

    result = patch_execution.execute_approved_patch(_incident(), _proposal())
    assert result.status == "DRAFT_PR_CREATED"
    assert result.reused is False
    assert result.commit_sha == "fix-commit"
    assert state["ref_posts"] == 1
    assert state["pr_posts"] == 1


def test_existing_exact_branch_and_pr_are_reused_without_write(monkeypatch) -> None:
    _patch_common(monkeypatch)
    calls = {"writes": 0, "ref_posts": 0, "pr_posts": 0}

    monkeypatch.setattr(
        patch_execution,
        "_optional_get",
        lambda client, path, params=None: {"object": {"sha": "existing-fix-commit"}},
    )

    def api(client, method, path, json=None, params=None):
        if method == "GET" and path.endswith("/repos/omghotekar01-dotcom/KURUKSHETRA-2.O"):
            return {"default_branch": "main"}
        if method == "GET" and "/git/ref/heads/main" in path:
            return {"object": {"sha": "base-sha"}}
        if method == "GET" and "/contents/README.md" in path:
            if params and params.get("ref", "").startswith("incident-fix/"):
                return _file("fixed\n")
            return _file("broken\n")
        if method == "GET" and path.endswith("/pulls"):
            return [
                {
                    "number": 17,
                    "html_url": "https://github.com/example/repo/pull/17",
                    "state": "open",
                    "head": {"ref": "incident-fix/inc-test123-patch-abc123"},
                }
            ]
        if method == "PUT":
            calls["writes"] += 1
        if method == "POST" and path.endswith("/git/refs"):
            calls["ref_posts"] += 1
        if method == "POST" and path.endswith("/pulls"):
            calls["pr_posts"] += 1
        raise AssertionError((method, path, params))

    monkeypatch.setattr(patch_execution, "_api", api)

    result = patch_execution.execute_approved_patch(_incident(), _proposal())
    assert result.status == "DRAFT_PR_CREATED"
    assert result.reused is True
    assert result.commit_sha == "existing-fix-commit"
    assert result.draft_pr_number == 17
    assert calls == {"writes": 0, "ref_posts": 0, "pr_posts": 0}

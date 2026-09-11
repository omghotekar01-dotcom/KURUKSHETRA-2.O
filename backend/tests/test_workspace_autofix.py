from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.workspace_autofix import (
    REPO_ROOT,
    _safe_file,
    autofix_target,
    propose_fix,
    reset_target,
    scan_target,
)


client = TestClient(app)
TARGET_ID = "broken-auth-api"


def test_autofix_routes_are_mounted() -> None:
    response = client.get("/api/v1/autofix/targets")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["id"] == TARGET_ID for item in payload)


def test_apply_requires_exact_preview_first(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    reset_target(TARGET_ID)

    response = client.post(f"/api/v1/autofix/{TARGET_ID}/apply")

    assert response.status_code == 409
    assert "Preview the exact fix" in response.json()["detail"]


def test_preview_then_apply_uses_reviewed_proposal(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    reset_target(TARGET_ID)

    preview = client.post(f"/api/v1/autofix/{TARGET_ID}/proposal")
    assert preview.status_code == 200
    reviewed = preview.json()
    assert reviewed["strategy"] == "DETERMINISTIC_SAFE_RULE"
    assert reviewed["writes_files"] is False

    applied = client.post(f"/api/v1/autofix/{TARGET_ID}/apply")
    assert applied.status_code == 200
    result = applied.json()
    assert result["final_status"] == "FIXED"
    assert result["proposal"]["file_path"] == reviewed["file_path"]
    assert result["proposal"]["before"] == reviewed["before"]
    assert result["proposal"]["after"] == reviewed["after"]
    assert result["proposal"]["diff"] == reviewed["diff"]
    assert any("exact previously previewed proposal" in item for item in result["audit"])

    reset_target(TARGET_ID)


def test_reset_invalidates_reviewed_proposal(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    client.post(f"/api/v1/autofix/{TARGET_ID}/reset")
    preview = client.post(f"/api/v1/autofix/{TARGET_ID}/proposal")
    assert preview.status_code == 200

    reset = client.post(f"/api/v1/autofix/{TARGET_ID}/reset")
    assert reset.status_code == 200

    applied = client.post(f"/api/v1/autofix/{TARGET_ID}/apply")
    assert applied.status_code == 409
    assert "No reviewed proposal" in applied.json()["detail"]


def test_changed_workspace_rejects_stale_reviewed_proposal(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    reset = client.post(f"/api/v1/autofix/{TARGET_ID}/reset")
    assert reset.status_code == 200
    workspace = Path(reset.json()["workspace_path"])

    preview = client.post(f"/api/v1/autofix/{TARGET_ID}/proposal")
    assert preview.status_code == 200

    source_path = workspace / "app.py"
    source = source_path.read_text(encoding="utf-8")
    source_path.write_text(source.replace('scheme.lower() != "token"', 'scheme.lower() != "legacy"'), encoding="utf-8")

    applied = client.post(f"/api/v1/autofix/{TARGET_ID}/apply")
    assert applied.status_code == 409
    assert "Workspace changed after diagnosis" in applied.json()["detail"]
    assert 'scheme.lower() != "legacy"' in source_path.read_text(encoding="utf-8")

    reset_target(TARGET_ID)


def test_real_demo_target_fails_then_is_fixed_and_proven(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFIX_AI_ENABLED", "false")
    reset = reset_target(TARGET_ID)
    assert reset.verification.passed is False
    assert reset.diagnosis.status == "BUG_CONFIRMED"
    assert reset.diagnosis.file_path == "app.py"
    assert reset.diagnosis.expected_value == "bearer"
    assert reset.diagnosis.observed_value == "token"

    proposal = propose_fix(TARGET_ID)
    assert proposal.writes_files is False
    assert proposal.strategy == "DETERMINISTIC_SAFE_RULE"
    assert '-    if scheme.lower() != "token":' in proposal.diff
    assert '+    if scheme.lower() != "bearer":' in proposal.diff

    result = autofix_target(TARGET_ID)
    assert result.applied is True
    assert result.rolled_back is False
    assert result.final_status == "FIXED"
    assert result.before_verification.passed is False
    assert result.after_verification.passed is True
    assert result.after_verification.exit_code == 0

    healthy = scan_target(TARGET_ID)
    assert healthy.verification.passed is True
    assert healthy.diagnosis.status == "HEALTHY"

    reset_again = reset_target(TARGET_ID)
    assert reset_again.verification.passed is False


def test_safe_file_rejects_workspace_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="outside"):
        _safe_file(workspace, "../outside.txt")


def test_demo_workspace_is_inside_repository_root() -> None:
    scan = scan_target(TARGET_ID)
    assert Path(scan.workspace_path).is_relative_to(REPO_ROOT)
    assert all("baseline" not in item.path for item in scan.files)

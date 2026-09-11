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


def test_real_demo_target_fails_then_is_fixed_and_proven() -> None:
    reset = reset_target(TARGET_ID)
    assert reset.verification.passed is False
    assert reset.diagnosis.status == "BUG_CONFIRMED"
    assert reset.diagnosis.file_path == "app.py"
    assert reset.diagnosis.expected_value == "bearer"
    assert reset.diagnosis.observed_value == "token"

    proposal = propose_fix(TARGET_ID)
    assert proposal.writes_files is False
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

from pathlib import Path

import pytest

from app.schemas.workspace import AdhocFileInput, AdhocIntakeRequest, WorkspaceFixProposal
from app.services import workspace_intake
from app.services.workspace_ai import WorkspaceAIAttempt


def _isolate_sessions(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workspace_intake, "SESSION_ROOT", tmp_path / "intake")
    workspace_intake._sessions.clear()


def test_judge_intake_rejects_path_escape(tmp_path: Path, monkeypatch) -> None:
    _isolate_sessions(tmp_path, monkeypatch)
    payload = AdhocIntakeRequest(
        problem="Attached code has a failing authentication regression.",
        files=[AdhocFileInput(path="../secret.py", content="x = 1\n")],
    )
    with pytest.raises(ValueError, match="Unsafe file path"):
        workspace_intake.create_intake(payload)


def test_static_intake_retrieves_rag_without_executing_code(tmp_path: Path, monkeypatch) -> None:
    _isolate_sessions(tmp_path, monkeypatch)
    payload = AdhocIntakeRequest(
        problem="Valid Bearer authentication receives 401 Unauthorized after a deployment.",
        files=[
            AdhocFileInput(path="app.py", content="SCHEME = 'token'\n"),
            AdhocFileInput(path="notes.txt", content="Authorization: Bearer demo-valid-token\n"),
        ],
        trusted_test_execution=False,
    )
    state = workspace_intake.create_intake(payload)
    assert state.execution_mode == "STATIC_ONLY"
    assert state.before_verification.passed is True
    assert any(hit.component == "Authentication" for hit in state.knowledge)
    assert "No user-supplied code was executed" in state.before_verification.output


def test_trusted_uploaded_pytest_can_fail_then_pass_after_exact_reviewed_patch(tmp_path: Path, monkeypatch) -> None:
    _isolate_sessions(tmp_path, monkeypatch)
    broken = "def add(a, b):\n    return a - b\n"
    fixed = "def add(a, b):\n    return a + b\n"
    payload = AdhocIntakeRequest(
        problem="add(2, 3) should return 5, but the implementation subtracts.",
        files=[
            AdhocFileInput(path="calc.py", content=broken),
            AdhocFileInput(path="test_calc.py", content="from calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"),
        ],
        trusted_test_execution=True,
    )
    state = workspace_intake.create_intake(payload)
    assert state.execution_mode == "TRUSTED_PYTEST"
    assert state.before_verification.passed is False

    reviewed = WorkspaceFixProposal(
        target_id=state.session_id,
        file_path="calc.py",
        summary="Correct the arithmetic operator required by the failing test.",
        before=broken,
        after=fixed,
        diff="-    return a - b\n+    return a + b\n",
        confidence=0.82,
        writes_files=False,
        strategy="AI_GROUNDED",
        reasoning_provider="ollama-local",
        reasoning_model="qwen3:4b",
    )
    result = workspace_intake.apply_intake_fix(state.session_id, reviewed)
    assert result.final_status == "VERIFIED_FIXED"
    assert result.after_verification.passed is True
    assert result.rolled_back is False
    assert result.patched_files["calc.py"] == fixed


def test_generic_intake_fails_closed_without_model_candidate(tmp_path: Path, monkeypatch) -> None:
    _isolate_sessions(tmp_path, monkeypatch)
    payload = AdhocIntakeRequest(
        problem="The attached function returns the wrong value for a known input.",
        files=[AdhocFileInput(path="sample.py", content="def value():\n    return 1\n")],
    )
    state = workspace_intake.create_intake(payload)
    monkeypatch.setattr(
        workspace_intake,
        "propose_file_patch",
        lambda **kwargs: WorkspaceAIAttempt(proposal=None, fallback_reason="local model offline"),
    )
    proposal = workspace_intake.propose_intake_fix(state.session_id)
    assert proposal.strategy == "NONE"
    assert proposal.diff == ""
    assert "refusing" in proposal.summary.lower() or "no safe" in proposal.summary.lower()
    assert proposal.fallback_reason == "local model offline"

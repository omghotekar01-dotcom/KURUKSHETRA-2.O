import json

from app.schemas.workspace import (
    CommandEvidence,
    ModelRuntimeStatus,
    WorkspaceDiagnosis,
    WorkspaceScanResult,
    WorkspaceTarget,
)
from app.services.workspace_ai import propose_file_patch, propose_workspace_patch


def _scan() -> WorkspaceScanResult:
    return WorkspaceScanResult(
        target=WorkspaceTarget(
            id="broken-auth-api",
            name="Broken auth",
            description="demo",
            relative_path="demo",
            problem="Bearer auth returns 401",
            proof="pytest",
            validator="python -m pytest -q",
        ),
        workspace_path="/safe/demo",
        files=[],
        verification=CommandEvidence(
            command="python -m pytest -q",
            exit_code=1,
            output="expected 200 but received 401",
            passed=False,
            duration_ms=10,
        ),
        diagnosis=WorkspaceDiagnosis(
            target_id="broken-auth-api",
            status="BUG_CONFIRMED",
            summary="auth scheme mismatch",
            file_path="app.py",
            line_number=2,
            expected_value="bearer",
            observed_value="token",
            confidence=0.99,
        ),
        safe_boundary="workspace only",
    )


def test_local_model_candidate_is_bounded_to_supplied_file(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="LOCAL_OLLAMA",
        provider="ollama-local",
        model="qwen3:4b",
        ready=True,
        endpoint="http://localhost:11434/v1",
        note="ready",
    )
    monkeypatch.setattr("app.services.workspace_ai.get_model_runtime_status", lambda: runtime)

    model_payload = {
        "file_path": "app.py",
        "search": 'scheme.lower() != "token"',
        "replace": 'scheme.lower() != "bearer"',
        "explanation": "Align the parser with the Bearer contract proven by the failing test.",
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps({"message": {"content": json.dumps(model_payload)}}).encode("utf-8")

    def fake_urlopen(request, timeout):
        assert request.full_url == "http://localhost:11434/api/chat"
        assert timeout >= 15
        body = json.loads(request.data.decode("utf-8"))
        assert body["model"] == "qwen3:4b"
        assert body["stream"] is False
        assert body["format"] == "json"
        assert body["keep_alive"] == "15m"
        assert body["think"] is False
        assert body["options"]["num_predict"] == 768
        return FakeResponse()

    monkeypatch.setattr("app.services.workspace_ai.urlopen", fake_urlopen)
    attempt = propose_workspace_patch(
        _scan(),
        {
            "app.py": 'x = 1\nif scheme.lower() != "token":\n    reject()\n',
            "test_app.py": 'headers={"Authorization": "Bearer demo-valid-token"}\n',
        },
    )

    assert attempt.proposal is not None
    assert attempt.proposal.strategy == "AI_GROUNDED"
    assert attempt.proposal.reasoning_provider == "ollama-local"
    assert '+if scheme.lower() != "bearer"' in attempt.proposal.diff


def test_model_cannot_patch_file_that_was_not_supplied(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="LOCAL_OLLAMA",
        provider="ollama-local",
        model="qwen3:4b",
        ready=True,
        endpoint="http://localhost:11434/v1",
        note="ready",
    )
    monkeypatch.setattr("app.services.workspace_ai.get_model_runtime_status", lambda: runtime)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            payload = {
                "file_path": "../../.ssh/config",
                "search": "a",
                "replace": "b",
                "explanation": "unsafe",
            }
            return json.dumps({"message": {"content": json.dumps(payload)}}).encode("utf-8")

    monkeypatch.setattr("app.services.workspace_ai.urlopen", lambda request, timeout: FakeResponse())
    attempt = propose_workspace_patch(_scan(), {"app.py": "abc"})

    assert attempt.proposal is None
    assert "rejected" in (attempt.fallback_reason or "")


def test_judge_intake_uses_exact_bearer_fallback_when_model_is_unavailable(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="DETERMINISTIC_FALLBACK",
        provider="deterministic",
        model="evidence-rules-v1",
        ready=True,
        endpoint=None,
        note="local model unavailable",
    )
    monkeypatch.setattr("app.services.workspace_ai.get_model_runtime_status", lambda: runtime)
    verification = CommandEvidence(
        command="python -m pytest -q",
        exit_code=1,
        output='assert authenticate("Bearer demo-valid-token") is True\nwhere False = authenticate("Bearer demo-valid-token")',
        passed=False,
        duration_ms=20,
    )

    attempt = propose_file_patch(
        target_id="JDG-DEMO",
        problem="Valid authentication should pass the supplied trusted test.",
        file_contents={
            "app.py": 'def authenticate(value):\n    scheme, token = value.split(" ", 1)\n    if scheme.lower() != "token":\n        return False\n    return token == "demo-valid-token"\n',
            "test_app.py": 'from app import authenticate\n\ndef test_valid_bearer_token():\n    assert authenticate("Bearer demo-valid-token") is True\n',
        },
        verification=verification,
        knowledge=[],
    )

    assert attempt.proposal is not None
    assert attempt.proposal.strategy == "DETERMINISTIC_SAFE_RULE"
    assert attempt.proposal.reasoning_provider == "deterministic-fallback"
    assert '-    if scheme.lower() != "token"' in attempt.proposal.diff
    assert '+    if scheme.lower() != "bearer"' in attempt.proposal.diff
    assert "DETERMINISTIC FALLBACK" in (attempt.proposal.fallback_reason or "")


def test_judge_intake_returns_guidance_instead_of_empty_response(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="DETERMINISTIC_FALLBACK",
        provider="deterministic",
        model="evidence-rules-v1",
        ready=True,
        endpoint=None,
        note="local model unavailable",
    )
    monkeypatch.setattr("app.services.workspace_ai.get_model_runtime_status", lambda: runtime)
    verification = CommandEvidence(
        command="python -m pytest -q",
        exit_code=1,
        output="assert value() == 2",
        passed=False,
        duration_ms=10,
    )

    attempt = propose_file_patch(
        target_id="JDG-GENERIC",
        problem="The attached function returns the wrong value.",
        file_contents={"sample.py": "def value():\n    return 1\n"},
        verification=verification,
        knowledge=[],
    )

    assert attempt.proposal is not None
    assert attempt.proposal.strategy == "NONE"
    assert attempt.proposal.diff == ""
    assert attempt.proposal.summary.strip()
    assert "Evidence fallback" in attempt.proposal.summary
    assert "EVIDENCE FALLBACK" in (attempt.proposal.fallback_reason or "")

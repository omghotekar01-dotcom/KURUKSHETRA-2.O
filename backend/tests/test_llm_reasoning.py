import json
from pathlib import Path
from urllib.error import URLError

from app.repositories.incidents import IncidentStore
from app.schemas.incident import IncidentIn, KnowledgeMatch
from app.services.llm_reasoning import synthesize_grounded_reasoning
from app.services.triage import triage_incident


def _record(tmp_path: Path):
    payload = IncidentIn(
        title="401 after deployment",
        description="Protected API requests fail after a signing configuration change.",
        logs=["JWT signature verification failed"],
    )
    store = IncidentStore(tmp_path / "incidents.db")
    return store.create(payload, triage_incident(payload))


def _matches() -> list[KnowledgeMatch]:
    return [
        KnowledgeMatch(
            id="RB-AUTH-001",
            component="Authentication",
            issue="JWT signature mismatch",
            fix="Align the token signing and verification configuration.",
            source="runbook",
            score=0.82,
        )
    ]


def _response_content() -> dict:
    return {
        "title": "Signing and verification configuration may be misaligned",
        "rationale": "The retrieved authentication runbook matches the observed JWT signature failure.",
        "next_diagnostic": "Compare signing and verification key identifiers in the active runtime configuration.",
        "remediation_summary": "Align the signing and verification configuration after confirming the mismatch.",
        "remediation_steps": ["Confirm the active key identifiers.", "Prepare the smallest reviewed configuration correction."],
    }


class FakeResponse:
    def __init__(self, content: dict):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps({"choices": [{"message": {"content": json.dumps(self.content)}}]}).encode("utf-8")


def test_grounded_llm_adapter_accepts_valid_https_response(tmp_path: Path, monkeypatch) -> None:
    record = _record(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example.test/v1")
    monkeypatch.setenv("LLM_MODEL", "judge-model")
    monkeypatch.setenv("LLM_PROVIDER", "test-provider")

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://llm.example.test/v1/chat/completions"
        assert 2.0 <= timeout <= 20.0
        return FakeResponse(_response_content())

    monkeypatch.setattr("app.services.llm_reasoning.urlopen", fake_urlopen)
    result = synthesize_grounded_reasoning(record, _matches(), repository_context=None)

    assert result.payload is not None
    assert result.payload["title"] == _response_content()["title"]
    assert result.provider == "test-provider"
    assert result.model == "judge-model"
    assert result.fallback_reason is None


def test_default_provider_is_zero_cost_local_ollama(tmp_path: Path, monkeypatch) -> None:
    record = _record(tmp_path)
    for key in ("LLM_PROVIDER", "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "OLLAMA_BASE_URL", "OLLAMA_MODEL", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    def fake_urlopen(request, timeout):
        assert request.full_url == "http://localhost:11434/v1/chat/completions"
        body = json.loads(request.data.decode("utf-8"))
        assert body["model"] == "qwen3:4b"
        return FakeResponse(_response_content())

    monkeypatch.setattr("app.services.llm_reasoning.urlopen", fake_urlopen)
    result = synthesize_grounded_reasoning(record, _matches(), repository_context=None)

    assert result.payload is not None
    assert result.provider == "ollama-local"
    assert result.model == "qwen3:4b"


def test_auto_provider_falls_from_local_ollama_to_configured_gemini(tmp_path: Path, monkeypatch) -> None:
    record = _record(tmp_path)
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    monkeypatch.setenv("GEMINI_API_KEY", "free-tier-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    calls: list[str] = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if request.full_url.startswith("http://localhost:11434"):
            raise URLError("ollama offline")
        assert request.full_url == "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        return FakeResponse(_response_content())

    monkeypatch.setattr("app.services.llm_reasoning.urlopen", fake_urlopen)
    result = synthesize_grounded_reasoning(record, _matches(), repository_context=None)

    assert result.payload is not None
    assert result.provider == "gemini-free-tier"
    assert result.model == "gemini-test"
    assert len(calls) == 2


def test_remote_plain_http_llm_endpoint_fails_closed(tmp_path: Path, monkeypatch) -> None:
    record = _record(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_BASE_URL", "http://remote.example.test/v1")
    monkeypatch.setenv("LLM_MODEL", "judge-model")
    monkeypatch.setenv("LLM_PROVIDER", "test-provider")
    called = False

    def fake_urlopen(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("unsafe remote endpoint must not be called")

    monkeypatch.setattr("app.services.llm_reasoning.urlopen", fake_urlopen)
    result = synthesize_grounded_reasoning(record, _matches(), repository_context=None)

    assert result.payload is None
    assert result.provider == "deterministic"
    assert "ValueError" in (result.fallback_reason or "")
    assert called is False


def test_local_plain_http_llm_endpoint_is_allowed_for_local_models(tmp_path: Path, monkeypatch) -> None:
    record = _record(tmp_path)
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "local-model")

    class BrokenLocalResponse:
        def __enter__(self):
            raise TimeoutError("local model not running")

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("app.services.llm_reasoning.urlopen", lambda request, timeout: BrokenLocalResponse())
    result = synthesize_grounded_reasoning(record, _matches(), repository_context=None)

    assert result.payload is None
    assert result.provider == "deterministic"
    assert "deterministic evidence reasoning used" in (result.fallback_reason or "")

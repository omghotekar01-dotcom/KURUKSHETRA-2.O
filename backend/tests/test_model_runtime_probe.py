import json
from urllib.error import URLError

from app.schemas.workspace import ModelRuntimeStatus
from app.services import model_runtime


def test_live_ollama_probe_calls_chat_completions(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="LOCAL_OLLAMA",
        provider="ollama-local",
        model="qwen3:4b",
        ready=True,
        endpoint="http://localhost:11434/v1",
        note="ready",
    )
    monkeypatch.setattr(model_runtime, "get_model_runtime_status", lambda: runtime)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": "READY"}}]}).encode("utf-8")

    def fake_urlopen(request, timeout):
        assert request.full_url == "http://localhost:11434/v1/chat/completions"
        body = json.loads(request.data.decode("utf-8"))
        assert body["model"] == "qwen3:4b"
        assert timeout == 12
        return FakeResponse()

    monkeypatch.setattr(model_runtime, "urlopen", fake_urlopen)
    result = model_runtime.probe_model_runtime()
    assert result.connected is True
    assert result.provider == "ollama-local"
    assert result.model == "qwen3:4b"
    assert result.reply == "READY"


def test_ollama_status_uses_native_tags_when_openai_models_route_is_unavailable(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:4b")

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(self.payload).encode("utf-8")

    def fake_urlopen(request, timeout):
        assert timeout == 2.0
        if request.full_url.endswith("/v1/models"):
            raise URLError("compatibility route unavailable")
        assert request.full_url == "http://localhost:11434/api/tags"
        return FakeResponse({"models": [{"name": "qwen3:4b"}]})

    monkeypatch.setattr(model_runtime, "urlopen", fake_urlopen)
    result = model_runtime._ollama_status()
    assert result.ready is True
    assert result.endpoint == "http://localhost:11434/v1"
    assert "native" in result.note


def test_live_ollama_probe_falls_back_to_native_chat(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="LOCAL_OLLAMA",
        provider="ollama-local",
        model="qwen3:4b",
        ready=True,
        endpoint="http://localhost:11434/v1",
        note="ready",
    )
    monkeypatch.setattr(model_runtime, "get_model_runtime_status", lambda: runtime)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps({"message": {"content": "READY_NATIVE"}}).encode("utf-8")

    def fake_urlopen(request, timeout):
        if request.full_url.endswith("/v1/chat/completions"):
            raise URLError("route unavailable")
        assert request.full_url == "http://localhost:11434/api/chat"
        assert timeout == 12
        return FakeResponse()

    monkeypatch.setattr(model_runtime, "urlopen", fake_urlopen)
    result = model_runtime.probe_model_runtime()
    assert result.connected is True
    assert result.reply == "READY_NATIVE"
    assert "native Ollama" in result.note


def test_probe_reports_no_live_model_for_deterministic_fallback(monkeypatch) -> None:
    runtime = ModelRuntimeStatus(
        mode="DETERMINISTIC_FALLBACK",
        provider="deterministic",
        model="evidence-rules-v1",
        ready=True,
        endpoint=None,
        note="fallback",
    )
    monkeypatch.setattr(model_runtime, "get_model_runtime_status", lambda: runtime)
    result = model_runtime.probe_model_runtime()
    assert result.connected is False
    assert "No live model" in result.note

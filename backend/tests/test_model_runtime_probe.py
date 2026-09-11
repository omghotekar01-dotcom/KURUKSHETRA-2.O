import json

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

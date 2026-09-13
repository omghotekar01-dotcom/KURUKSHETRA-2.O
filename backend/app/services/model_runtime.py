from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.schemas.workspace import ModelProbeResult, ModelRuntimeStatus


def _setting(name: str) -> str:
    return os.getenv(name, "").strip()


def _ollama_urls() -> tuple[str, str]:
    """Return (native_root, openai_compatible_base) for local Ollama.

    Users commonly configure either http://localhost:11434 or
    http://localhost:11434/v1. Normalising both here prevents the runtime probe
    from accidentally producing /v1/v1 or /v1/api URLs.
    """
    configured = (_setting("OLLAMA_BASE_URL") or "http://localhost:11434/v1").rstrip("/")
    if configured.endswith("/v1"):
        root = configured[:-3].rstrip("/")
        openai_base = configured
    elif configured.endswith("/api"):
        root = configured[:-4].rstrip("/")
        openai_base = root + "/v1"
    else:
        root = configured
        openai_base = root + "/v1"
    return root, openai_base


def _model_names(payload: object) -> set[str]:
    names: set[str] = set()
    if not isinstance(payload, dict):
        return names

    # Ollama OpenAI compatibility: {"data": [{"id": "qwen3:4b"}]}
    data = payload.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("id"):
                names.add(str(item["id"]))

    # Ollama native API: {"models": [{"name": "qwen3:4b", "model": ...}]}
    models = payload.get("models")
    if isinstance(models, list):
        for item in models:
            if not isinstance(item, dict):
                continue
            for key in ("name", "model"):
                if item.get(key):
                    names.add(str(item[key]))
    return names


def _model_available(requested: str, available: set[str]) -> bool:
    requested_lower = requested.lower()
    for candidate in available:
        normalized = candidate.strip().lower()
        if normalized == requested_lower:
            return True
        if normalized.removesuffix(":latest") == requested_lower.removesuffix(":latest"):
            return True
        if ":" not in requested_lower and normalized.startswith(requested_lower + ":"):
            return True
    return False


def _read_json(url: str, *, timeout: float = 2.0) -> object:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - localhost Ollama endpoint
        return json.loads(response.read().decode("utf-8"))


def _ollama_status() -> ModelRuntimeStatus:
    root, openai_base = _ollama_urls()
    model = _setting("OLLAMA_MODEL") or _setting("LLM_MODEL") or "qwen3:4b"

    available: set[str] = set()
    reachable_path = ""
    failures: list[str] = []
    for label, endpoint in (
        ("OpenAI-compatible", openai_base + "/models"),
        ("native", root + "/api/tags"),
    ):
        try:
            available.update(_model_names(_read_json(endpoint)))
            reachable_path = label
            break
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as exc:
            failures.append(type(exc).__name__)

    if not reachable_path:
        detail = ", ".join(failures) or "connection error"
        return ModelRuntimeStatus(
            mode="LOCAL_OLLAMA",
            provider="ollama-local",
            model=model,
            ready=False,
            endpoint=openai_base,
            note=(
                "Ollama is not reachable on the configured local endpoint "
                f"({detail}). Start the Ollama app/service, then run setup-local-ai.bat. "
                "The verified deterministic repair engine remains available meanwhile."
            ),
        )

    ready = _model_available(model, available)
    note = (
        f"Local Ollama is reachable through its {reachable_path} API and {model} is installed."
        if ready
        else (
            f"Local Ollama is reachable through its {reachable_path} API, but {model} was not found. "
            f"Installed models: {', '.join(sorted(available)) or 'none reported'}. Run: ollama pull {model}"
        )
    )
    return ModelRuntimeStatus(
        mode="LOCAL_OLLAMA",
        provider="ollama-local",
        model=model,
        ready=ready,
        endpoint=openai_base,
        note=note,
    )


def _gemini_status() -> ModelRuntimeStatus | None:
    gemini_key = _setting("GEMINI_API_KEY")
    if not gemini_key:
        return None
    return ModelRuntimeStatus(
        mode="GEMINI_FREE",
        provider="gemini-free-tier",
        model=_setting("GEMINI_MODEL") or "gemini-3.5-flash-lite",
        ready=True,
        endpoint=_setting("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta/openai",
        note=(
            "Gemini is configured as the primary AI runtime. If a live Gemini request fails in auto mode, "
            "the reasoning pipeline may fall back to local Ollama/Qwen and then deterministic evidence rules."
        ),
    )


def get_model_runtime_status() -> ModelRuntimeStatus:
    """Return the preferred live model runtime.

    AUTO priority is intentionally Gemini first, then local Ollama/Qwen, then
    deterministic verified fallbacks. Explicit LLM_PROVIDER values still force
    the selected provider.
    """
    requested = (_setting("LLM_PROVIDER") or "auto").lower()

    # Gemini is the first choice whenever AUTO is used and a key is configured.
    if requested in {"auto", "gemini", "gemini_free"}:
        gemini = _gemini_status()
        if gemini is not None:
            return gemini
        if requested != "auto":
            return ModelRuntimeStatus(
                mode="GEMINI_FREE",
                provider="gemini-free-tier",
                model=_setting("GEMINI_MODEL") or "gemini-3.5-flash-lite",
                ready=False,
                endpoint=_setting("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com/v1beta/openai",
                note="Gemini is selected but GEMINI_API_KEY is missing.",
            )

    # Local Qwen/Ollama is the second choice in AUTO mode and the forced choice
    # when an Ollama/local provider is explicitly requested.
    if requested in {"auto", "ollama", "local", "local_ollama"}:
        local = _ollama_status()
        if local.ready or requested != "auto":
            return local

    return ModelRuntimeStatus(
        mode="DETERMINISTIC_FALLBACK",
        provider="deterministic",
        model="evidence-rules-v1",
        ready=True,
        endpoint=None,
        note=(
            "No live model service is connected. Configure Gemini first or start Ollama/Qwen. "
            "Verified scan, bounded repair, rollback and validation remain available where deterministic rules exist."
        ),
    )


def _openai_chat_probe(runtime: ModelRuntimeStatus, api_key: str) -> tuple[str, int]:
    payload = {
        "model": runtime.model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "You are a connectivity probe. Reply with exactly READY and nothing else.",
            },
            {"role": "user", "content": "Connectivity check."},
        ],
    }
    request = Request(
        (runtime.endpoint or "").rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    with urlopen(request, timeout=12) as response:  # noqa: S310 - local Ollama or configured HTTPS provider
        raw = json.loads(response.read().decode("utf-8"))
    reply = str(raw["choices"][0]["message"]["content"]).strip()
    return reply, int((time.perf_counter() - started) * 1000)


def _ollama_native_chat_probe(model: str) -> tuple[str, int]:
    root, _ = _ollama_urls()
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": "Reply with exactly READY and nothing else."},
            {"role": "user", "content": "Connectivity check."},
        ],
        "options": {"temperature": 0},
    }
    request = Request(
        root + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urlopen(request, timeout=12) as response:  # noqa: S310 - localhost Ollama endpoint
        raw = json.loads(response.read().decode("utf-8"))
    message = raw.get("message") if isinstance(raw, dict) else None
    if not isinstance(message, dict):
        raise KeyError("message")
    reply = str(message["content"]).strip()
    return reply, int((time.perf_counter() - started) * 1000)


def probe_model_runtime() -> ModelProbeResult:
    runtime = get_model_runtime_status()
    if runtime.mode == "DETERMINISTIC_FALLBACK" or not runtime.endpoint:
        return ModelProbeResult(
            connected=False,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=0,
            reply="",
            note="No live model is connected. Configure Gemini or start the local Ollama/Qwen fallback.",
        )

    api_key = "ollama" if runtime.mode == "LOCAL_OLLAMA" else _setting("GEMINI_API_KEY")
    if runtime.mode == "GEMINI_FREE" and not api_key:
        return ModelProbeResult(
            connected=False,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=0,
            reply="",
            note="Gemini is selected but GEMINI_API_KEY is missing.",
        )

    started = time.perf_counter()
    first_error: Exception | None = None
    try:
        reply, latency_ms = _openai_chat_probe(runtime, api_key)
        return ModelProbeResult(
            connected=True,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=latency_ms,
            reply=reply[:160],
            note="Live chat-completions request succeeded. This proves the preferred model endpoint is actually callable.",
        )
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        first_error = exc

    if runtime.mode == "LOCAL_OLLAMA":
        try:
            reply, latency_ms = _ollama_native_chat_probe(runtime.model)
            return ModelProbeResult(
                connected=True,
                provider=runtime.provider,
                model=runtime.model,
                latency_ms=latency_ms,
                reply=reply[:160],
                note="Live native Ollama chat request succeeded after the OpenAI-compatible probe was unavailable.",
            )
        except (HTTPError, URLError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
            pass

    latency_ms = int((time.perf_counter() - started) * 1000)
    error_name = type(first_error).__name__ if first_error is not None else "ConnectionError"
    if runtime.mode == "GEMINI_FREE":
        recovery = "Confirm the Gemini API key, free-tier quota, internet connection and configured model."
    else:
        recovery = f"Confirm Ollama is running and {runtime.model} is installed."

    return ModelProbeResult(
        connected=False,
        provider=runtime.provider,
        model=runtime.model,
        latency_ms=latency_ms,
        reply="",
        note=(
            f"Live model probe failed ({error_name}). {recovery} "
            "The deterministic engine remains available, and normal auto-mode reasoning can use the next configured provider."
        ),
    )

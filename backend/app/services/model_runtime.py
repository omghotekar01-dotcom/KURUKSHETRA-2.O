from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.schemas.workspace import ModelProbeResult, ModelRuntimeStatus


def _setting(name: str) -> str:
    return os.getenv(name, "").strip()


def _ollama_status() -> ModelRuntimeStatus:
    base_url = _setting("OLLAMA_BASE_URL") or "http://localhost:11434/v1"
    model = _setting("OLLAMA_MODEL") or _setting("LLM_MODEL") or "qwen3:4b"
    endpoint = base_url.rstrip("/") + "/models"
    try:
        request = Request(endpoint, headers={"Accept": "application/json"})
        with urlopen(request, timeout=1.25) as response:  # noqa: S310 - localhost-only default endpoint
            payload = json.loads(response.read().decode("utf-8"))
        available = {item.get("id") for item in payload.get("data", []) if isinstance(item, dict)}
        ready = model in available or any(str(item).startswith(model + ":") for item in available if item)
        note = (
            f"Local Ollama is reachable and {model} is installed."
            if ready
            else f"Local Ollama is reachable, but {model} is not installed. Run: ollama pull {model}"
        )
        return ModelRuntimeStatus(
            mode="LOCAL_OLLAMA",
            provider="ollama-local",
            model=model,
            ready=ready,
            endpoint=base_url,
            note=note,
        )
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return ModelRuntimeStatus(
            mode="LOCAL_OLLAMA",
            provider="ollama-local",
            model=model,
            ready=False,
            endpoint=base_url,
            note="Ollama is not reachable. The verified deterministic repair engine remains available without any API.",
        )


def get_model_runtime_status() -> ModelRuntimeStatus:
    requested = (_setting("LLM_PROVIDER") or "auto").lower()

    if requested in {"auto", "ollama", "local", "local_ollama"}:
        local = _ollama_status()
        if local.ready or requested != "auto":
            return local

    gemini_key = _setting("GEMINI_API_KEY")
    if requested in {"auto", "gemini", "gemini_free"} and gemini_key:
        return ModelRuntimeStatus(
            mode="GEMINI_FREE",
            provider="gemini-free-tier",
            model=_setting("GEMINI_MODEL") or "gemini-3.8-flash",
            ready=True,
            endpoint="https://generativelanguage.googleapis.com/v1beta/openai",
            note="Gemini is configured as a free-tier fallback. Usage remains subject to Google's current free-tier quotas.",
        )

    return ModelRuntimeStatus(
        mode="DETERMINISTIC_FALLBACK",
        provider="deterministic",
        model="evidence-rules-v1",
        ready=True,
        endpoint=None,
        note="No model service is required for the proof loop: scan, exact bounded repair, rollback and verification still work locally.",
    )


def probe_model_runtime() -> ModelProbeResult:
    runtime = get_model_runtime_status()
    if runtime.mode == "DETERMINISTIC_FALLBACK" or not runtime.endpoint:
        return ModelProbeResult(
            connected=False,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=0,
            reply="",
            note="No live model is connected. Start Ollama/Qwen or configure the optional Gemini free-tier fallback.",
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
        runtime.endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=12) as response:  # noqa: S310 - local Ollama or Gemini HTTPS
            raw = json.loads(response.read().decode("utf-8"))
        reply = str(raw["choices"][0]["message"]["content"]).strip()
        latency_ms = int((time.perf_counter() - started) * 1000)
        return ModelProbeResult(
            connected=True,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=latency_ms,
            reply=reply[:160],
            note="Live chat-completions request succeeded. This proves the configured model endpoint is actually callable.",
        )
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return ModelProbeResult(
            connected=False,
            provider=runtime.provider,
            model=runtime.model,
            latency_ms=latency_ms,
            reply="",
            note=f"Live model probe failed ({type(exc).__name__}). The deterministic engine remains available, but generic judge intake will fail closed rather than guess.",
        )

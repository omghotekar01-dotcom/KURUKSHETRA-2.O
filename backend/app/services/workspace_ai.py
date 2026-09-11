from __future__ import annotations

import difflib
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.schemas.workspace import WorkspaceFixProposal, WorkspaceScanResult
from app.services.model_runtime import get_model_runtime_status


@dataclass(frozen=True)
class WorkspaceAIAttempt:
    proposal: WorkspaceFixProposal | None
    fallback_reason: str | None


def _bounded(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[bounded]"


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("model response is not a JSON object")
    return payload


def propose_workspace_patch(scan: WorkspaceScanResult, file_contents: dict[str, str]) -> WorkspaceAIAttempt:
    """Ask the configured zero-cost model for one exact search/replace candidate.

    Model output is data only. It cannot choose commands or paths outside the supplied file map,
    and the caller must still verify the edit with the predefined validator.
    """

    runtime = get_model_runtime_status()
    if not runtime.ready or runtime.mode == "DETERMINISTIC_FALLBACK" or not runtime.endpoint:
        return WorkspaceAIAttempt(proposal=None, fallback_reason=runtime.note)

    api_key = "ollama" if runtime.mode == "LOCAL_OLLAMA" else os.getenv("GEMINI_API_KEY", "").strip()
    if runtime.mode == "GEMINI_FREE" and not api_key:
        return WorkspaceAIAttempt(proposal=None, fallback_reason="Gemini free-tier key is not configured.")

    compact_files = {
        path: _bounded(content, 7000)
        for path, content in list(file_contents.items())[:8]
    }
    evidence = {
        "problem": scan.target.problem,
        "validator": scan.verification.command,
        "failing_output": _bounded(scan.verification.output, 6500),
        "deterministic_diagnosis": scan.diagnosis.model_dump(),
        "files": compact_files,
    }
    system_prompt = (
        "You are a bounded code-repair planner. Use only the supplied failing test evidence and file contents. "
        "Return JSON only with exactly these keys: file_path, search, replace, explanation. "
        "file_path must be one of the supplied files. search must be an exact contiguous substring copied from that file, "
        "and it must be the smallest useful edit target. replace is the corrected text. Never return shell commands, paths not supplied, "
        "new files, secrets, markdown fences, or claims that tests passed. Prefer a one-line or very small repair."
    )
    request_payload = {
        "model": runtime.model,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(evidence, ensure_ascii=False)},
        ],
    }
    endpoint = runtime.endpoint.rstrip("/") + "/chat/completions"
    request = Request(
        endpoint,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        timeout_seconds = max(2.0, min(float(os.getenv("AUTOFIX_LLM_TIMEOUT_SECONDS", "12")), 25.0))
    except ValueError:
        timeout_seconds = 12.0

    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - runtime endpoint is local Ollama or Gemini HTTPS
            raw = json.loads(response.read().decode("utf-8"))
        payload = _extract_json(raw["choices"][0]["message"]["content"])

        file_path = payload.get("file_path")
        search = payload.get("search")
        replace = payload.get("replace")
        explanation = payload.get("explanation")
        if not all(isinstance(value, str) for value in (file_path, search, replace, explanation)):
            raise ValueError("model patch fields must be strings")
        if file_path not in file_contents:
            raise ValueError("model selected a file outside the supplied workspace evidence")
        if not search or len(search) > 2000 or len(replace) > 3000:
            raise ValueError("model patch exceeds bounded edit limits")

        before = file_contents[file_path]
        if before.count(search) != 1:
            raise ValueError("model search text is stale or ambiguous")
        after = before.replace(search, replace, 1)
        if after == before:
            raise ValueError("model patch makes no change")

        diff = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
            )
        )
        return WorkspaceAIAttempt(
            proposal=WorkspaceFixProposal(
                target_id=scan.target.id,
                file_path=file_path,
                summary=_bounded(explanation.strip(), 900),
                before=before,
                after=after,
                diff=diff,
                confidence=min(scan.diagnosis.confidence, 0.85),
                writes_files=False,
                strategy="AI_GROUNDED",
                reasoning_provider=runtime.provider,
                reasoning_model=runtime.model,
                fallback_reason=None,
            ),
            fallback_reason=None,
        )
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return WorkspaceAIAttempt(
            proposal=None,
            fallback_reason=f"{runtime.provider} candidate unavailable or rejected ({type(exc).__name__}); using deterministic safe repair.",
        )

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from threading import Lock

from app.schemas.workspace import (
    AdhocFixResult,
    AdhocIntakeRequest,
    AdhocWorkspaceState,
    CommandEvidence,
    WorkspaceFile,
    WorkspaceFixProposal,
    WorkspaceKnowledgeHit,
)
from app.services.model_runtime import get_model_runtime_status
from app.services.workspace_ai import propose_file_patch

SESSION_ROOT = Path(tempfile.gettempdir()) / "ai-agentic-bug-router-intake"
RUNBOOKS = Path(__file__).resolve().parents[2] / "data" / "runbooks.json"
ALLOWED_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml", ".md", ".txt"}
BLOCKED_PARTS = {".git", ".ssh", ".aws", ".azure", ".config", ".venv", "venv", "node_modules", "__pycache__"}
MAX_SESSION_AGE_SECONDS = 2 * 60 * 60
TOKEN_RE = re.compile(r"[a-z0-9_+-]+")
STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "with"}


@dataclass
class _SessionMeta:
    problem: str
    trusted_test_execution: bool
    created_at: float


_sessions: dict[str, _SessionMeta] = {}
_sessions_lock = Lock()


def _cleanup_old_sessions() -> None:
    now = time.time()
    stale: list[str] = []
    with _sessions_lock:
        for session_id, meta in _sessions.items():
            if now - meta.created_at > MAX_SESSION_AGE_SECONDS:
                stale.append(session_id)
        for session_id in stale:
            _sessions.pop(session_id, None)
    for session_id in stale:
        shutil.rmtree(SESSION_ROOT / session_id, ignore_errors=True)


def _validate_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    path = PurePosixPath(normalized)
    if (
        not normalized
        or normalized.startswith("/")
        or normalized.startswith("//")
        or re.match(r"^[A-Za-z]:/", normalized)
        or path.is_absolute()
        or ".." in path.parts
    ):
        raise ValueError(f"Unsafe file path: {value}")
    if any(part.lower() in BLOCKED_PARTS for part in path.parts):
        raise ValueError(f"Blocked file path: {value}")
    if Path(path.name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {value}")
    return path.as_posix()


def _session_dir(session_id: str) -> Path:
    with _sessions_lock:
        if session_id not in _sessions:
            raise KeyError(session_id)
    root = (SESSION_ROOT / session_id).resolve()
    expected_root = SESSION_ROOT.resolve()
    try:
        root.relative_to(expected_root)
    except ValueError as exc:
        raise ValueError("Session path escaped the intake root") from exc
    if not root.exists():
        raise FileNotFoundError(f"Intake session no longer exists: {session_id}")
    return root


def _safe_session_file(root: Path, relative_path: str) -> Path:
    normalized = _validate_relative_path(relative_path)
    candidate = (root / normalized).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("File escaped the intake workspace") from exc
    return candidate


def _safe_exec_env() -> dict[str, str]:
    allowed = {"systemroot", "windir", "path", "temp", "tmp", "pathext", "comspec", "home"}
    env = {key: value for key, value in os.environ.items() if key.lower() in allowed and value}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _has_pytest_contract(root: Path) -> bool:
    return any(path.is_file() and path.suffix.lower() == ".py" and path.name.startswith("test_") for path in root.rglob("*.py"))


def _clear_python_caches(root: Path) -> None:
    """Best-effort cleanup of session-local bytecode caches before trusted verification."""

    for cache_dir in sorted(root.rglob("__pycache__"), reverse=True):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    for pyc in root.rglob("*.pyc"):
        if not pyc.is_file():
            continue
        try:
            pyc.unlink()
        except OSError:
            pass


def _run_pytest(root: Path) -> CommandEvidence:
    _clear_python_caches(root)
    command = [sys.executable, "-B", "-m", "pytest", "-q", "--cache-clear"]
    started = time.perf_counter()
    pycache_root = Path(tempfile.mkdtemp(prefix="router-pycache-"))
    env = _safe_exec_env()
    env["PYTHONPYCACHEPREFIX"] = str(pycache_root)
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
            env=env,
        )
        output = (completed.stdout + "\n" + completed.stderr).strip()
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        output = f"Trusted pytest timed out after 25 seconds.\n{stdout}\n{stderr}".strip()
        exit_code = 124
    finally:
        shutil.rmtree(pycache_root, ignore_errors=True)
    duration_ms = int((time.perf_counter() - started) * 1000)
    return CommandEvidence(
        command=f"{Path(sys.executable).name} -B -m pytest -q --cache-clear [TRUSTED USER-SUPPLIED TESTS]",
        exit_code=exit_code,
        output=output[-12_000:],
        passed=exit_code == 0,
        duration_ms=duration_ms,
    )


def _run_static_checks(root: Path) -> CommandEvidence:
    started = time.perf_counter()
    checked = 0
    failures: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        suffix = path.suffix.lower()
        try:
            text = path.read_text(encoding="utf-8")
            if suffix == ".py":
                compile(text, str(path), "exec")
                checked += 1
            elif suffix == ".json":
                json.loads(text)
                checked += 1
        except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"{path.relative_to(root).as_posix()}: {exc}")
    duration_ms = int((time.perf_counter() - started) * 1000)
    if failures:
        output = "Static validation failed:\n" + "\n".join(failures[:20])
        return CommandEvidence(command="static syntax/schema validation", exit_code=1, output=output, passed=False, duration_ms=duration_ms)
    output = (
        f"Static validation passed for {checked} Python/JSON file(s). "
        "No user-supplied code was executed; functional recovery is not proven in STATIC_ONLY mode."
    )
    return CommandEvidence(command="static syntax/schema validation", exit_code=0, output=output, passed=True, duration_ms=duration_ms)


def _verify(root: Path, trusted_requested: bool) -> tuple[CommandEvidence, str]:
    if trusted_requested and _has_pytest_contract(root):
        return _run_pytest(root), "TRUSTED_PYTEST"
    return _run_static_checks(root), "STATIC_ONLY"


def _tokens(text: str) -> Counter[str]:
    return Counter(token for token in TOKEN_RE.findall(text.lower()) if token not in STOP_WORDS)


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left).intersection(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _retrieve_knowledge(problem: str, contents: dict[str, str]) -> list[WorkspaceKnowledgeHit]:
    entries = json.loads(RUNBOOKS.read_text(encoding="utf-8"))
    evidence_text = " ".join([problem, *contents.keys(), *[value[:1200] for value in contents.values()]])
    query = _tokens(evidence_text)
    hits: list[WorkspaceKnowledgeHit] = []
    for entry in entries:
        score = _cosine(query, _tokens(f"{entry['component']} {entry['issue']} {entry['fix']}"))
        if score < 0.08:
            continue
        hits.append(
            WorkspaceKnowledgeHit(
                id=entry["id"],
                component=entry["component"],
                issue=entry["issue"],
                fix=entry["fix"],
                source=entry["source"],
                score=round(min(1.0, score), 3),
            )
        )
    hits.sort(key=lambda item: item.score, reverse=True)
    return hits[:3]


def _contents(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = path.read_text(encoding="utf-8", errors="replace")
        if len(result) >= 12:
            break
    return result


def _state(session_id: str) -> AdhocWorkspaceState:
    root = _session_dir(session_id)
    with _sessions_lock:
        meta = _sessions[session_id]
    contents = _contents(root)
    verification, mode = _verify(root, meta.trusted_test_execution)
    return AdhocWorkspaceState(
        session_id=session_id,
        problem=meta.problem,
        files=[WorkspaceFile(path=path, size_bytes=len(content.encode("utf-8"))) for path, content in contents.items()],
        knowledge=_retrieve_knowledge(meta.problem, contents),
        before_verification=verification,
        execution_mode=mode,
        model_runtime=get_model_runtime_status(),
        safe_boundary=(
            "Judge-supplied files are copied into an isolated temporary workspace. The model receives only bounded uploaded text. "
            "Writes stay inside that copy. User-supplied Python tests execute only when Trusted test execution is explicitly enabled."
        ),
    )


def create_intake(payload: AdhocIntakeRequest) -> AdhocWorkspaceState:
    _cleanup_old_sessions()
    SESSION_ROOT.mkdir(parents=True, exist_ok=True)
    session_id = "JDG-" + uuid.uuid4().hex[:10]
    root = SESSION_ROOT / session_id
    root.mkdir(parents=True, exist_ok=False)

    seen: set[str] = set()
    try:
        for item in payload.files:
            relative = _validate_relative_path(item.path)
            if relative in seen:
                raise ValueError(f"Duplicate uploaded file path: {relative}")
            seen.add(relative)
            destination = _safe_session_file_unregistered(root, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(item.content, encoding="utf-8")
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise

    with _sessions_lock:
        _sessions[session_id] = _SessionMeta(
            problem=payload.problem.strip(),
            trusted_test_execution=payload.trusted_test_execution,
            created_at=time.time(),
        )
    return _state(session_id)


def _safe_session_file_unregistered(root: Path, relative_path: str) -> Path:
    normalized = _validate_relative_path(relative_path)
    candidate = (root / normalized).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("File escaped the intake workspace") from exc
    return candidate


def get_intake(session_id: str) -> AdhocWorkspaceState:
    return _state(session_id)


def propose_intake_fix(session_id: str) -> WorkspaceFixProposal:
    state = _state(session_id)
    root = _session_dir(session_id)
    contents = _contents(root)
    attempt = propose_file_patch(
        target_id=session_id,
        problem=state.problem,
        file_contents=contents,
        verification=state.before_verification,
        knowledge=state.knowledge,
    )
    if attempt.proposal is not None:
        return attempt.proposal
    return WorkspaceFixProposal(
        target_id=session_id,
        file_path="",
        summary="No safe generic patch was produced. Connect Qwen/Ollama or provide stronger evidence/tests instead of guessing.",
        before="",
        after="",
        diff="",
        confidence=0.0,
        strategy="NONE",
        reasoning_provider=state.model_runtime.provider,
        reasoning_model=state.model_runtime.model,
        fallback_reason=attempt.fallback_reason or state.model_runtime.note,
    )


def apply_intake_fix(session_id: str, reviewed: WorkspaceFixProposal) -> AdhocFixResult:
    state = _state(session_id)
    root = _session_dir(session_id)
    if reviewed.target_id != session_id or reviewed.writes_files or reviewed.strategy == "NONE":
        raise ValueError("Reviewed intake proposal is not an executable no-write preview")
    target = _safe_session_file(root, reviewed.file_path)
    original = target.read_text(encoding="utf-8")
    if original != reviewed.before:
        raise ValueError("Uploaded workspace changed after preview; generate a fresh proposal")

    audit = [
        "Judge intake session containment verified.",
        "Operator approval is bound to the exact previously previewed patch.",
        f"Execution mode: {state.execution_mode}.",
        f"Planner: {reviewed.strategy} via {reviewed.reasoning_provider}/{reviewed.reasoning_model}.",
    ]
    target.write_text(reviewed.after, encoding="utf-8")
    with _sessions_lock:
        meta = _sessions[session_id]
    after, mode = _verify(root, meta.trusted_test_execution)
    audit.append(f"Post-patch validator: {after.command}; exit {after.exit_code}.")

    if not after.passed:
        target.write_text(original, encoding="utf-8")
        restored, _ = _verify(root, meta.trusted_test_execution)
        audit.append("Validation failed; exact original uploaded file was restored.")
        return AdhocFixResult(
            state=state,
            proposal=reviewed.model_copy(update={"writes_files": True}),
            applied=True,
            rolled_back=True,
            after_verification=restored,
            final_status="ROLLED_BACK",
            patched_files={reviewed.file_path: original},
            audit=audit,
        )

    if mode == "TRUSTED_PYTEST" and not state.before_verification.passed:
        status = "VERIFIED_FIXED"
        audit.append("The trusted failing pytest contract now passes; functional recovery is proven for the supplied tests.")
    else:
        status = "STATIC_CHECK_PASSED"
        audit.append("Static/syntax checks pass, but functional recovery is not claimed without a failing trusted test baseline.")

    return AdhocFixResult(
        state=state,
        proposal=reviewed.model_copy(update={"writes_files": True}),
        applied=True,
        rolled_back=False,
        after_verification=after,
        final_status=status,
        patched_files={reviewed.file_path: reviewed.after},
        audit=audit,
    )

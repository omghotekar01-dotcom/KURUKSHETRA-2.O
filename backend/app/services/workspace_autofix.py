from __future__ import annotations

import difflib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from app.schemas.workspace import (
    CommandEvidence,
    WorkspaceDiagnosis,
    WorkspaceFile,
    WorkspaceFixProposal,
    WorkspaceFixResult,
    WorkspaceScanResult,
    WorkspaceTarget,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WORKSPACE_ROOT = REPO_ROOT
BLOCKED_PARTS = {
    ".git",
    ".ssh",
    ".aws",
    ".azure",
    ".config",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "baseline",
}
ALLOWED_SUFFIXES = {".py", ".json", ".md", ".txt", ".toml", ".yaml", ".yml", ".js", ".ts", ".tsx"}
MAX_FILE_BYTES = 256_000
MAX_OUTPUT_CHARS = 12_000


_TARGETS: dict[str, WorkspaceTarget] = {
    "broken-auth-api": WorkspaceTarget(
        id="broken-auth-api",
        name="Broken Bearer Authentication API",
        description=(
            "A real FastAPI service whose protected endpoint rejects the standard Bearer scheme after an auth-parser regression."
        ),
        relative_path="demo_targets/broken_auth_api",
        problem="Users provide a valid Bearer token but /profile returns HTTP 401.",
        proof="A real pytest fails before repair and the exact same pytest passes after the source file is corrected.",
        validator=f"{Path(sys.executable).name} -m pytest -q",
    ),
}


def _configured_workspace_root() -> Path:
    configured = os.getenv("AUTOFIX_WORKSPACE_ROOT", "").strip()
    root = Path(configured).expanduser() if configured else DEFAULT_WORKSPACE_ROOT
    return root.resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _target_path(target: WorkspaceTarget) -> Path:
    root = _configured_workspace_root()
    path = (root / target.relative_path).resolve()
    if not _is_relative_to(path, root):
        raise ValueError("Target resolves outside the configured workspace root")
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Workspace target does not exist: {path}")
    return path


def get_target(target_id: str) -> WorkspaceTarget:
    target = _TARGETS.get(target_id)
    if target is None:
        raise KeyError(target_id)
    return target


def list_targets() -> list[WorkspaceTarget]:
    return list(_TARGETS.values())


def _safe_file(target_root: Path, relative_path: str) -> Path:
    candidate = (target_root / relative_path).resolve()
    if not _is_relative_to(candidate, target_root.resolve()):
        raise ValueError("File resolves outside the selected workspace")
    if any(part.lower() in BLOCKED_PARTS for part in candidate.parts):
        raise ValueError("Access to secret/system/build directories is blocked")
    return candidate


def _inventory(target_root: Path) -> list[WorkspaceFile]:
    files: list[WorkspaceFile] = []
    root = target_root.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part.lower() in BLOCKED_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            continue
        files.append(WorkspaceFile(path=relative.as_posix(), size_bytes=size))
    return files[:200]


def _run_validator(target_root: Path) -> CommandEvidence:
    command = [sys.executable, "-m", "pytest", "-q"]
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=target_root,
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        output = (completed.stdout + "\n" + completed.stderr).strip()
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        output = f"Validator timed out after 25 seconds.\n{stdout}\n{stderr}".strip()
        exit_code = 124

    duration_ms = int((time.perf_counter() - started) * 1000)
    if len(output) > MAX_OUTPUT_CHARS:
        output = output[-MAX_OUTPUT_CHARS:]
    return CommandEvidence(
        command=f"{Path(sys.executable).name} -m pytest -q",
        exit_code=exit_code,
        output=output,
        passed=exit_code == 0,
        duration_ms=duration_ms,
    )


def _line_number(text: str, needle: str) -> int | None:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    return None


def _diagnose_auth_target(target: WorkspaceTarget, target_root: Path, verification: CommandEvidence) -> WorkspaceDiagnosis:
    source_path = _safe_file(target_root, "app.py")
    test_path = _safe_file(target_root, "test_app.py")
    source = source_path.read_text(encoding="utf-8")
    tests = test_path.read_text(encoding="utf-8")

    test_scheme_match = re.search(r'Authorization["\']\s*:\s*["\']([A-Za-z]+)\s+', tests)
    code_scheme_match = re.search(r'scheme\.lower\(\)\s*!=\s*["\']([A-Za-z]+)["\']', source)

    if verification.passed:
        return WorkspaceDiagnosis(
            target_id=target.id,
            status="HEALTHY",
            summary="The selected workspace currently passes its real validator.",
            confidence=1.0,
            evidence=["pytest exit code = 0"],
        )

    if test_scheme_match and code_scheme_match:
        expected = test_scheme_match.group(1).lower()
        observed = code_scheme_match.group(1).lower()
        if expected != observed:
            needle = f'scheme.lower() != "{observed}"'
            return WorkspaceDiagnosis(
                target_id=target.id,
                status="BUG_CONFIRMED",
                summary=(
                    f"Authentication contract mismatch: tests/clients send {expected.title()} credentials, "
                    f"but the parser accepts {observed.title()}."
                ),
                file_path="app.py",
                line_number=_line_number(source, needle),
                evidence=[
                    "The validator reproduces an HTTP 401 for a token that the contract marks valid.",
                    f"test_app.py sends Authorization: {expected.title()} demo-valid-token.",
                    f"app.py explicitly rejects every scheme except {observed.title()}.",
                ],
                expected_value=expected,
                observed_value=observed,
                confidence=0.99,
            )

    return WorkspaceDiagnosis(
        target_id=target.id,
        status="UNRESOLVED",
        summary="The validator fails, but the bounded deterministic analyzer could not prove a safe exact edit.",
        confidence=0.0,
        evidence=["pytest exit code != 0", "No allowlisted exact repair rule matched the observed source/test contract."],
    )


def scan_target(target_id: str) -> WorkspaceScanResult:
    target = get_target(target_id)
    target_root = _target_path(target)
    verification = _run_validator(target_root)
    diagnosis = _diagnose_auth_target(target, target_root, verification)
    return WorkspaceScanResult(
        target=target,
        workspace_path=str(target_root),
        files=_inventory(target_root),
        verification=verification,
        diagnosis=diagnosis,
        safe_boundary=(
            "Read/write access is restricted to this selected workspace. The agent cannot follow model-generated shell commands "
            "or write outside the configured workspace root."
        ),
    )


def _proposal_from_scan(scan: WorkspaceScanResult) -> WorkspaceFixProposal:
    diagnosis = scan.diagnosis
    target_root = Path(scan.workspace_path)
    if diagnosis.status != "BUG_CONFIRMED" or not diagnosis.file_path:
        return WorkspaceFixProposal(
            target_id=scan.target.id,
            file_path=diagnosis.file_path or "",
            summary="No bounded automatic edit is available for this state.",
            before="",
            after="",
            diff="",
            confidence=diagnosis.confidence,
            writes_files=False,
        )

    source_path = _safe_file(target_root, diagnosis.file_path)
    before = source_path.read_text(encoding="utf-8")
    observed = diagnosis.observed_value or ""
    expected = diagnosis.expected_value or ""
    old = f'scheme.lower() != "{observed}"'
    new = f'scheme.lower() != "{expected}"'
    if before.count(old) != 1:
        raise ValueError("Expected repair location is stale or ambiguous")
    after = before.replace(old, new, 1)
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{diagnosis.file_path}",
            tofile=f"b/{diagnosis.file_path}",
        )
    )
    return WorkspaceFixProposal(
        target_id=scan.target.id,
        file_path=diagnosis.file_path,
        summary=f"Align the auth parser with the {expected.title()} scheme required by the tested API contract.",
        before=before,
        after=after,
        diff=diff,
        confidence=diagnosis.confidence,
        writes_files=False,
    )


def propose_fix(target_id: str) -> WorkspaceFixProposal:
    return _proposal_from_scan(scan_target(target_id))


def autofix_target(target_id: str) -> WorkspaceFixResult:
    target = get_target(target_id)
    before_scan = scan_target(target_id)
    proposal = _proposal_from_scan(before_scan)
    audit = [
        "Workspace path containment verified.",
        f"Pre-fix validator exited with {before_scan.verification.exit_code}.",
        f"Diagnosis status: {before_scan.diagnosis.status}.",
    ]

    if before_scan.verification.passed:
        return WorkspaceFixResult(
            target=target,
            before_verification=before_scan.verification,
            diagnosis=before_scan.diagnosis,
            proposal=proposal,
            applied=False,
            rolled_back=False,
            after_verification=before_scan.verification,
            final_status="ALREADY_HEALTHY",
            audit=audit,
        )

    if before_scan.diagnosis.status != "BUG_CONFIRMED" or not proposal.file_path or not proposal.after:
        return WorkspaceFixResult(
            target=target,
            before_verification=before_scan.verification,
            diagnosis=before_scan.diagnosis,
            proposal=proposal,
            applied=False,
            rolled_back=False,
            after_verification=before_scan.verification,
            final_status="UNRESOLVED",
            audit=audit + ["No file was changed because a safe exact repair was not proven."],
        )

    target_root = Path(before_scan.workspace_path)
    source_path = _safe_file(target_root, proposal.file_path)
    original = source_path.read_text(encoding="utf-8")
    if original != proposal.before:
        raise ValueError("Workspace changed after diagnosis; refusing stale repair")

    source_path.write_text(proposal.after, encoding="utf-8")
    audit.append(f"Applied exact bounded edit to {proposal.file_path}.")
    after_verification = _run_validator(target_root)
    audit.append(f"Post-fix validator exited with {after_verification.exit_code}.")

    if not after_verification.passed:
        source_path.write_text(original, encoding="utf-8")
        audit.append("Verification failed; original file restored automatically.")
        rollback_verification = _run_validator(target_root)
        return WorkspaceFixResult(
            target=target,
            before_verification=before_scan.verification,
            diagnosis=before_scan.diagnosis,
            proposal=proposal.model_copy(update={"writes_files": True}),
            applied=True,
            rolled_back=True,
            after_verification=rollback_verification,
            final_status="ROLLED_BACK",
            audit=audit,
        )

    audit.append("The same real validator now passes; repair is proven for the tested regression.")
    return WorkspaceFixResult(
        target=target,
        before_verification=before_scan.verification,
        diagnosis=before_scan.diagnosis,
        proposal=proposal.model_copy(update={"writes_files": True}),
        applied=True,
        rolled_back=False,
        after_verification=after_verification,
        final_status="FIXED",
        audit=audit,
    )


def reset_target(target_id: str) -> WorkspaceScanResult:
    target = get_target(target_id)
    target_root = _target_path(target)
    baseline_path = (target_root / "baseline" / "app.py.txt").resolve()
    if not _is_relative_to(baseline_path, target_root):
        raise ValueError("Baseline resolves outside workspace")
    source_path = _safe_file(target_root, "app.py")
    source_path.write_text(baseline_path.read_text(encoding="utf-8"), encoding="utf-8")
    return scan_target(target_id)

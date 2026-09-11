from __future__ import annotations

import difflib
import os
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
from app.services.workspace_ai import propose_workspace_patch


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
MODEL_SOURCE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".json"}
MAX_FILE_BYTES = 256_000
MAX_OUTPUT_CHARS = 12_000


_TARGETS: dict[str, WorkspaceTarget] = {
    "broken-auth-api": WorkspaceTarget(
        id="broken-auth-api",
        name="Broken Bearer Authentication API",
        description="A real FastAPI service whose protected endpoint rejects the standard Bearer scheme after an auth-parser regression.",
        relative_path="demo_targets/broken_auth_api",
        problem="Users provide a valid Bearer token but /profile returns HTTP 401.",
        proof="A real pytest fails before repair and the exact same pytest passes after the source file is corrected.",
        validator=f"{Path(sys.executable).name} -m pytest -q",
    ),
    "broken-cart-total": WorkspaceTarget(
        id="broken-cart-total",
        name="Broken Cart Total",
        description="A real business-logic regression subtracts one paise from every cart total, including an empty cart.",
        relative_path="demo_targets/broken_cart_total",
        problem="Cart totals are consistently one paise too low and an empty cart returns -1 instead of 0.",
        proof="Real pytest assertions reproduce the wrong totals and the same tests must pass after repair.",
        validator=f"{Path(sys.executable).name} -m pytest -q",
    ),
    "broken-pagination": WorkspaceTarget(
        id="broken-pagination",
        name="Broken Pagination Boundary",
        description="A real off-by-one slice regression drops the last item from every requested page.",
        relative_path="demo_targets/broken_pagination",
        problem="A page configured for three records returns only two because the slice end boundary is wrong.",
        proof="Real pagination tests fail before repair and the exact same tests must pass afterward.",
        validator=f"{Path(sys.executable).name} -m pytest -q",
    ),
}


_RULES: dict[str, dict[str, object]] = {
    "broken-auth-api": {
        "source": "app.py",
        "old": 'scheme.lower() != "token"',
        "new": 'scheme.lower() != "bearer"',
        "expected": "bearer",
        "observed": "token",
        "summary": "Align the auth parser with the Bearer scheme required by the tested API contract.",
        "diagnosis": "Authentication contract mismatch: tests/clients send Bearer credentials, but the parser accepts Token.",
        "evidence": [
            "The validator reproduces HTTP 401 for a token that the contract marks valid.",
            "test_app.py sends Authorization: Bearer demo-valid-token.",
            "app.py explicitly rejects every scheme except Token.",
        ],
    },
    "broken-cart-total": {
        "source": "pricing.py",
        "old": "return sum(prices) - 1",
        "new": "return sum(prices)",
        "expected": "exact cart sum",
        "observed": "sum minus one",
        "summary": "Remove the unintended one-paise subtraction so the implementation matches the tested cart-total contract.",
        "diagnosis": "Business-logic contract mismatch: the implementation subtracts one from every cart total.",
        "evidence": [
            "The validator shows a cart expected to total 2000 is returned one unit low.",
            "The empty-cart acceptance test requires 0.",
            "pricing.py subtracts 1 unconditionally after summing the cart.",
        ],
    },
    "broken-pagination": {
        "source": "pagination.py",
        "old": "return items[start:end - 1]",
        "new": "return items[start:end]",
        "expected": "full end-exclusive slice",
        "observed": "end minus one",
        "summary": "Use the already computed end-exclusive boundary so every page returns its full requested size.",
        "diagnosis": "Pagination boundary mismatch: the code subtracts one from an already end-exclusive Python slice boundary.",
        "evidence": [
            "The validator shows a requested three-item page contains only two records.",
            "Both first-page and second-page acceptance tests reproduce the truncation.",
            "pagination.py computes end = start + page_size and then subtracts one again in the slice.",
        ],
    },
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
    relative_parts = candidate.relative_to(target_root.resolve()).parts
    if any(part.lower() in BLOCKED_PARTS for part in relative_parts):
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


def _diagnose_target(target: WorkspaceTarget, target_root: Path, verification: CommandEvidence) -> WorkspaceDiagnosis:
    rule = _RULES[target.id]
    source_name = str(rule["source"])
    source_path = _safe_file(target_root, source_name)
    source = source_path.read_text(encoding="utf-8")

    if verification.passed:
        return WorkspaceDiagnosis(
            target_id=target.id,
            status="HEALTHY",
            summary="The selected workspace currently passes its real validator.",
            confidence=1.0,
            evidence=["pytest exit code = 0"],
        )

    old = str(rule["old"])
    if source.count(old) == 1:
        return WorkspaceDiagnosis(
            target_id=target.id,
            status="BUG_CONFIRMED",
            summary=str(rule["diagnosis"]),
            file_path=source_name,
            line_number=_line_number(source, old),
            evidence=[str(item) for item in rule["evidence"]],
            expected_value=str(rule["expected"]),
            observed_value=str(rule["observed"]),
            confidence=0.99 if target.id == "broken-auth-api" else 0.97,
        )

    return WorkspaceDiagnosis(
        target_id=target.id,
        status="UNRESOLVED",
        summary="The validator fails, but the bounded deterministic analyzer could not prove a safe exact edit for this target state.",
        confidence=0.0,
        evidence=["pytest exit code != 0", "The expected allowlisted regression signature is absent or ambiguous."],
    )


def scan_target(target_id: str) -> WorkspaceScanResult:
    target = get_target(target_id)
    target_root = _target_path(target)
    verification = _run_validator(target_root)
    diagnosis = _diagnose_target(target, target_root, verification)
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


def _deterministic_proposal_from_scan(scan: WorkspaceScanResult, fallback_reason: str | None = None) -> WorkspaceFixProposal:
    diagnosis = scan.diagnosis
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
            strategy="NONE",
            fallback_reason=fallback_reason,
        )

    target_root = Path(scan.workspace_path)
    rule = _RULES[scan.target.id]
    source_path = _safe_file(target_root, diagnosis.file_path)
    before = source_path.read_text(encoding="utf-8")
    old = str(rule["old"])
    new = str(rule["new"])
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
        summary=str(rule["summary"]),
        before=before,
        after=after,
        diff=diff,
        confidence=diagnosis.confidence,
        writes_files=False,
        strategy="DETERMINISTIC_SAFE_RULE",
        reasoning_provider="deterministic",
        reasoning_model="source-test-contract-v2",
        fallback_reason=fallback_reason,
    )


def _model_file_contents(scan: WorkspaceScanResult) -> dict[str, str]:
    target_root = Path(scan.workspace_path)
    contents: dict[str, str] = {}
    for item in scan.files:
        if Path(item.path).suffix.lower() not in MODEL_SOURCE_SUFFIXES:
            continue
        path = _safe_file(target_root, item.path)
        contents[item.path] = path.read_text(encoding="utf-8", errors="replace")
        if len(contents) >= 8:
            break
    return contents


def _choose_proposal(scan: WorkspaceScanResult) -> WorkspaceFixProposal:
    if scan.verification.passed or scan.diagnosis.status != "BUG_CONFIRMED":
        return _deterministic_proposal_from_scan(scan)

    enabled = os.getenv("AUTOFIX_AI_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
    if not enabled:
        return _deterministic_proposal_from_scan(scan, "AI patch planning disabled; deterministic safe rule used.")

    attempt = propose_workspace_patch(scan, _model_file_contents(scan))
    if attempt.proposal is not None:
        return attempt.proposal
    return _deterministic_proposal_from_scan(scan, attempt.fallback_reason)


def propose_fix(target_id: str) -> WorkspaceFixProposal:
    return _choose_proposal(scan_target(target_id))


def _apply_candidate(target_root: Path, proposal: WorkspaceFixProposal) -> tuple[CommandEvidence, bool]:
    source_path = _safe_file(target_root, proposal.file_path)
    original = source_path.read_text(encoding="utf-8")
    if original != proposal.before:
        raise ValueError("Workspace changed after diagnosis; refusing stale repair")

    source_path.write_text(proposal.after, encoding="utf-8")
    verification = _run_validator(target_root)
    if verification.passed:
        return verification, False

    source_path.write_text(original, encoding="utf-8")
    return _run_validator(target_root), True


def autofix_target(target_id: str) -> WorkspaceFixResult:
    target = get_target(target_id)
    before_scan = scan_target(target_id)
    proposal = _choose_proposal(before_scan)
    audit = [
        "Workspace path containment verified.",
        f"Pre-fix validator exited with {before_scan.verification.exit_code}.",
        f"Diagnosis status: {before_scan.diagnosis.status}.",
        f"Repair planner: {proposal.strategy} via {proposal.reasoning_provider}/{proposal.reasoning_model}.",
    ]
    if proposal.fallback_reason:
        audit.append(proposal.fallback_reason)

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
    audit.append(f"Applied exact bounded edit to {proposal.file_path}.")
    after_verification, rolled_back = _apply_candidate(target_root, proposal)
    audit.append(f"Post-fix validator exited with {after_verification.exit_code}.")

    if after_verification.passed:
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

    if proposal.strategy == "AI_GROUNDED" and rolled_back:
        audit.append("AI candidate did not pass verification and was rolled back; trying deterministic safe repair.")
        fallback = _deterministic_proposal_from_scan(before_scan, "AI candidate failed real validation and was rolled back.")
        if fallback.file_path and fallback.after:
            audit.append(f"Applied deterministic fallback edit to {fallback.file_path}.")
            fallback_verification, fallback_rolled_back = _apply_candidate(target_root, fallback)
            audit.append(f"Deterministic fallback validator exited with {fallback_verification.exit_code}.")
            if fallback_verification.passed:
                audit.append("Deterministic fallback passed the same validator; repair is proven.")
                return WorkspaceFixResult(
                    target=target,
                    before_verification=before_scan.verification,
                    diagnosis=before_scan.diagnosis,
                    proposal=fallback.model_copy(update={"writes_files": True}),
                    applied=True,
                    rolled_back=False,
                    after_verification=fallback_verification,
                    final_status="FIXED",
                    audit=audit,
                )
            rolled_back = fallback_rolled_back
            after_verification = fallback_verification
            proposal = fallback

    audit.append("Verification did not pass; the original broken source state was restored.")
    return WorkspaceFixResult(
        target=target,
        before_verification=before_scan.verification,
        diagnosis=before_scan.diagnosis,
        proposal=proposal.model_copy(update={"writes_files": True}),
        applied=True,
        rolled_back=rolled_back,
        after_verification=after_verification,
        final_status="ROLLED_BACK",
        audit=audit,
    )


def reset_target(target_id: str) -> WorkspaceScanResult:
    target = get_target(target_id)
    target_root = _target_path(target)
    rule = _RULES[target_id]
    source_name = str(rule["source"])
    baseline_path = (target_root / "baseline" / f"{source_name}.txt").resolve()
    if not _is_relative_to(baseline_path, target_root):
        raise ValueError("Baseline resolves outside workspace")
    if not baseline_path.exists():
        raise FileNotFoundError(f"Reset baseline does not exist: {baseline_path}")
    source_path = _safe_file(target_root, source_name)
    source_path.write_text(baseline_path.read_text(encoding="utf-8"), encoding="utf-8")
    return scan_target(target_id)

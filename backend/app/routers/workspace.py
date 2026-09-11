from threading import Lock

from fastapi import APIRouter, HTTPException

from app.schemas.workspace import (
    AdhocFixResult,
    AdhocIntakeRequest,
    AdhocWorkspaceState,
    ModelProbeResult,
    ModelRuntimeStatus,
    WorkspaceFixProposal,
    WorkspaceFixResult,
    WorkspaceScanResult,
    WorkspaceTarget,
)
from app.services.model_runtime import get_model_runtime_status, probe_model_runtime
from app.services.workspace_autofix import list_targets, propose_fix, reset_target, scan_target
from app.services.workspace_intake import apply_intake_fix, create_intake, get_intake, propose_intake_fix
from app.services.workspace_review import apply_reviewed_proposal


router = APIRouter(prefix="/autofix", tags=["autofix"])

_reviewed_proposals: dict[str, WorkspaceFixProposal] = {}
_reviewed_proposals_lock = Lock()


def _review_key(target_id: str, *, intake: bool = False) -> str:
    return f"intake:{target_id}" if intake else target_id


@router.get("/targets", response_model=list[WorkspaceTarget])
def targets() -> list[WorkspaceTarget]:
    return list_targets()


@router.get("/model-runtime", response_model=ModelRuntimeStatus)
def model_runtime() -> ModelRuntimeStatus:
    return get_model_runtime_status()


@router.post("/model-runtime/probe", response_model=ModelProbeResult)
def model_runtime_probe() -> ModelProbeResult:
    return probe_model_runtime()


def _not_found_or_conflict(exc: Exception) -> HTTPException:
    if isinstance(exc, KeyError):
        return HTTPException(status_code=404, detail="Autofix target/session not found")
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=409, detail=str(exc))


def _store_reviewed(target_id: str, reviewed: WorkspaceFixProposal) -> None:
    with _reviewed_proposals_lock:
        _reviewed_proposals[target_id] = reviewed


def _consume_reviewed(target_id: str) -> WorkspaceFixProposal | None:
    with _reviewed_proposals_lock:
        return _reviewed_proposals.pop(target_id, None)


def _clear_reviewed(target_id: str) -> None:
    with _reviewed_proposals_lock:
        _reviewed_proposals.pop(target_id, None)


@router.post("/intake", response_model=AdhocWorkspaceState)
def intake(payload: AdhocIntakeRequest) -> AdhocWorkspaceState:
    try:
        return create_intake(payload)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.get("/intake/{session_id}", response_model=AdhocWorkspaceState)
def intake_state(session_id: str) -> AdhocWorkspaceState:
    try:
        return get_intake(session_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/intake/{session_id}/proposal", response_model=WorkspaceFixProposal)
def intake_proposal(session_id: str) -> WorkspaceFixProposal:
    key = _review_key(session_id, intake=True)
    _clear_reviewed(key)
    try:
        reviewed = propose_intake_fix(session_id)
        if reviewed.strategy != "NONE" and reviewed.diff:
            _store_reviewed(key, reviewed)
        return reviewed
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/intake/{session_id}/apply", response_model=AdhocFixResult)
def intake_apply(session_id: str) -> AdhocFixResult:
    key = _review_key(session_id, intake=True)
    reviewed = _consume_reviewed(key)
    if reviewed is None:
        raise HTTPException(
            status_code=409,
            detail="Preview the exact judge-intake fix before applying it. No reviewed proposal is armed for this session.",
        )
    try:
        return apply_intake_fix(session_id, reviewed)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/scan", response_model=WorkspaceScanResult)
def scan(target_id: str) -> WorkspaceScanResult:
    _clear_reviewed(target_id)
    try:
        return scan_target(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/proposal", response_model=WorkspaceFixProposal)
def proposal(target_id: str) -> WorkspaceFixProposal:
    _clear_reviewed(target_id)
    try:
        reviewed = propose_fix(target_id)
        _store_reviewed(target_id, reviewed)
        return reviewed
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/apply", response_model=WorkspaceFixResult)
def apply(target_id: str) -> WorkspaceFixResult:
    reviewed = _consume_reviewed(target_id)
    if reviewed is None:
        raise HTTPException(
            status_code=409,
            detail="Preview the exact fix before applying it. No reviewed proposal is currently armed for this target.",
        )
    try:
        return apply_reviewed_proposal(target_id, reviewed)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/reset", response_model=WorkspaceScanResult)
def reset(target_id: str) -> WorkspaceScanResult:
    _clear_reviewed(target_id)
    try:
        return reset_target(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc

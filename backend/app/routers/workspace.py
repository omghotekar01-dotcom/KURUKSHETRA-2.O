from threading import Lock

from fastapi import APIRouter, HTTPException

from app.schemas.workspace import (
    ModelRuntimeStatus,
    WorkspaceFixProposal,
    WorkspaceFixResult,
    WorkspaceScanResult,
    WorkspaceTarget,
)
from app.services.model_runtime import get_model_runtime_status
from app.services.workspace_autofix import list_targets, propose_fix, reset_target, scan_target
from app.services.workspace_review import apply_reviewed_proposal


router = APIRouter(prefix="/autofix", tags=["autofix"])

_reviewed_proposals: dict[str, WorkspaceFixProposal] = {}
_reviewed_proposals_lock = Lock()


@router.get("/targets", response_model=list[WorkspaceTarget])
def targets() -> list[WorkspaceTarget]:
    return list_targets()


@router.get("/model-runtime", response_model=ModelRuntimeStatus)
def model_runtime() -> ModelRuntimeStatus:
    return get_model_runtime_status()


def _not_found_or_conflict(exc: Exception) -> HTTPException:
    if isinstance(exc, KeyError):
        return HTTPException(status_code=404, detail="Autofix target not found")
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

from fastapi import APIRouter, HTTPException

from app.schemas.workspace import (
    ModelRuntimeStatus,
    WorkspaceFixProposal,
    WorkspaceFixResult,
    WorkspaceScanResult,
    WorkspaceTarget,
)
from app.services.model_runtime import get_model_runtime_status
from app.services.workspace_autofix import autofix_target, list_targets, propose_fix, reset_target, scan_target


router = APIRouter(prefix="/api/v1/autofix", tags=["autofix"])


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


@router.post("/{target_id}/scan", response_model=WorkspaceScanResult)
def scan(target_id: str) -> WorkspaceScanResult:
    try:
        return scan_target(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/proposal", response_model=WorkspaceFixProposal)
def proposal(target_id: str) -> WorkspaceFixProposal:
    try:
        return propose_fix(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/apply", response_model=WorkspaceFixResult)
def apply(target_id: str) -> WorkspaceFixResult:
    try:
        return autofix_target(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc


@router.post("/{target_id}/reset", response_model=WorkspaceScanResult)
def reset(target_id: str) -> WorkspaceScanResult:
    try:
        return reset_target(target_id)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        raise _not_found_or_conflict(exc) from exc

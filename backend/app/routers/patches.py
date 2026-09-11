from __future__ import annotations

from threading import Lock

from fastapi import APIRouter, HTTPException

from app.repositories.incidents import IncidentStore
from app.routers.evaluation import router as evaluation_router
from app.routers.workspace import router as workspace_router
from app.schemas.incident import ApprovalDecision, IncidentStatus, PatchProposalRequest
from app.schemas.patch import (
    PatchDecisionRequest,
    PatchExecutionResult,
    PatchMergeRequest,
    PatchMergeResult,
    PatchVerificationResult,
    ValidationCheck,
)
from app.services.github_context import GitHubContextUnavailable, collect_repository_context
from app.services.patch_execution import execute_approved_patch, patch_idempotency_key
from app.services.patch_proposal import PatchProposalUnavailable, build_patch_proposal
from app.services.patch_verification import PatchVerificationUnavailable, verify_patch_ci
from app.services.pull_request_merge import PatchMergeUnavailable, merge_verified_patch_pr

router = APIRouter(prefix="/api/v1", tags=["patch-remediation"])
router.include_router(evaluation_router)
router.include_router(workspace_router)
store = IncidentStore.from_env()

_approval_locks: dict[str, Lock] = {}
_approval_locks_guard = Lock()


def _same_exact_proposal(left, right) -> bool:
    return (
        left.proposal_id == right.proposal_id
        and left.repository == right.repository
        and left.base_commit == right.base_commit
        and left.file_path == right.file_path
        and left.hunk_header == right.hunk_header
        and left.before_lines == right.before_lines
        and left.after_lines == right.after_lines
    )


def _latest_event_metadata(incident, stage: str) -> dict:
    for event in reversed(incident.timeline):
        if event.stage == stage:
            return event.metadata
    return {}


def _lock_for(key: str) -> Lock:
    with _approval_locks_guard:
        return _approval_locks.setdefault(key, Lock())


def _existing_successful_execution(incident, proposal_id: str, idempotency_key: str) -> PatchExecutionResult | None:
    for event in reversed(incident.timeline):
        if event.stage != "PATCH_EXECUTION":
            continue
        metadata = event.metadata
        if metadata.get("proposal_id") != proposal_id:
            continue
        if metadata.get("status") != "DRAFT_PR_CREATED":
            continue
        stored_key = metadata.get("idempotency_key")
        if stored_key and stored_key != idempotency_key:
            continue

        repository = str(metadata.get("repository") or incident.incident.repo or "")
        branch = metadata.get("branch")
        validation = [ValidationCheck.model_validate(item) for item in metadata.get("validation", [])]
        return PatchExecutionResult(
            incident_id=incident.id,
            proposal_id=proposal_id,
            decision=ApprovalDecision.approve,
            status="DRAFT_PR_CREATED",
            message="Existing successful remediation reused. No duplicate branch, commit, validation write or pull request was created.",
            repository=repository,
            branch=branch,
            branch_url=metadata.get("branch_url") or (f"https://github.com/{repository}/tree/{branch}" if repository and branch else None),
            commit_sha=metadata.get("commit_sha"),
            draft_pr_number=metadata.get("draft_pr_number"),
            draft_pr_url=metadata.get("draft_pr_url"),
            validation=validation,
            incident_status=IncidentStatus.verifying,
            reused=True,
            idempotency_key=idempotency_key,
        )
    return None


def _existing_merge_result(incident, *, repository: str, draft_pr_number: int) -> PatchMergeResult | None:
    for event in reversed(incident.timeline):
        if event.stage != "PATCH_MERGED":
            continue
        metadata = event.metadata
        if str(metadata.get("repository") or "") != repository:
            continue
        if int(metadata.get("draft_pr_number") or 0) != draft_pr_number:
            continue
        return PatchMergeResult(
            incident_id=incident.id,
            repository=repository,
            draft_pr_number=draft_pr_number,
            merged=True,
            merge_sha=metadata.get("merge_sha"),
            merge_method=str(metadata.get("merge_method") or "squash"),
            reviewer=str(metadata.get("reviewer") or "human-reviewer"),
            message="This exact remediation pull request was already merged after human confirmation; no duplicate merge was attempted.",
            incident_status=IncidentStatus.verifying,
            runtime_verification_required=True,
        )
    return None


def _approve_patch(incident_id: str, payload: PatchDecisionRequest, idempotency_key: str) -> PatchExecutionResult:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    previous = _existing_successful_execution(incident, payload.proposal.proposal_id, idempotency_key)
    if previous is not None:
        store.append_event(
            incident_id,
            "PATCH_EXECUTION_REUSED",
            "Duplicate approval safely returned the existing remediation result.",
            {
                "proposal_id": payload.proposal.proposal_id,
                "idempotency_key": idempotency_key,
                "branch": previous.branch,
                "commit_sha": previous.commit_sha,
                "draft_pr_number": previous.draft_pr_number,
                "draft_pr_url": previous.draft_pr_url,
            },
        )
        store.set_status(incident_id, IncidentStatus.verifying)
        return previous

    try:
        context = collect_repository_context(incident)
        fresh = build_patch_proposal(
            incident,
            context,
            PatchProposalRequest(
                commit_sha=payload.proposal.base_commit,
                filename=payload.proposal.file_path,
                hunk_header=payload.proposal.hunk_header,
            ),
        )
    except (GitHubContextUnavailable, PatchProposalUnavailable) as exc:
        store.append_event(
            incident_id,
            "PATCH_STALE",
            "Patch approval blocked because live evidence could not reproduce the reviewed proposal.",
            {"proposal_id": payload.proposal.proposal_id, "reason": str(exc), "idempotency_key": idempotency_key},
        )
        raise HTTPException(status_code=409, detail=f"Reviewed patch is stale or unavailable: {exc}") from exc

    if not _same_exact_proposal(fresh, payload.proposal):
        store.append_event(
            incident_id,
            "PATCH_STALE",
            "Patch approval blocked because the live proposal changed since review.",
            {
                "proposal_id": payload.proposal.proposal_id,
                "fresh_proposal_id": fresh.proposal_id,
                "idempotency_key": idempotency_key,
            },
        )
        raise HTTPException(status_code=409, detail="Reviewed patch changed after live revalidation. Refresh evidence and review again.")

    store.append_event(
        incident_id,
        "PATCH_APPROVED",
        f"Exact patch proposal {fresh.proposal_id} approved by {payload.reviewer}.",
        {
            "proposal_id": fresh.proposal_id,
            "reviewer": payload.reviewer,
            "note": payload.note,
            "repository": fresh.repository,
            "file_path": fresh.file_path,
            "base_commit": fresh.base_commit,
            "idempotency_key": idempotency_key,
        },
    )
    store.set_status(incident_id, IncidentStatus.executing)

    result = execute_approved_patch(incident, fresh)
    store.append_event(
        incident_id,
        "PATCH_EXECUTION",
        result.message,
        {
            "proposal_id": result.proposal_id,
            "status": result.status,
            "repository": result.repository,
            "branch": result.branch,
            "branch_url": result.branch_url,
            "commit_sha": result.commit_sha,
            "draft_pr_number": result.draft_pr_number,
            "draft_pr_url": result.draft_pr_url,
            "validation": [check.model_dump() for check in result.validation],
            "reused": result.reused,
            "idempotency_key": result.idempotency_key or idempotency_key,
        },
    )
    store.set_status(incident_id, result.incident_status)
    return result


@router.post("/incidents/{incident_id}/patch-decision", response_model=PatchExecutionResult)
def decide_patch(incident_id: str, payload: PatchDecisionRequest) -> PatchExecutionResult:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    if payload.proposal.incident_id != incident_id:
        raise HTTPException(status_code=409, detail="Patch proposal does not belong to this incident.")
    if not incident.incident.repo:
        raise HTTPException(status_code=409, detail="Incident has no GitHub repository attached.")

    if payload.decision is ApprovalDecision.reject:
        store.append_event(
            incident_id,
            "PATCH_REJECTED",
            f"Patch proposal {payload.proposal.proposal_id} rejected by {payload.reviewer}.",
            {"proposal_id": payload.proposal.proposal_id, "reviewer": payload.reviewer, "note": payload.note},
        )
        refreshed = store.get(incident_id)
        status = refreshed.status if refreshed else incident.status
        return PatchExecutionResult(
            incident_id=incident_id,
            proposal_id=payload.proposal.proposal_id,
            decision=payload.decision,
            status="REJECTED",
            message="Patch proposal rejected. No repository write occurred.",
            repository=payload.proposal.repository,
            incident_status=status,
        )

    idempotency_key = patch_idempotency_key(incident_id, payload.proposal)
    with _lock_for(idempotency_key):
        return _approve_patch(incident_id, payload, idempotency_key)


@router.get("/incidents/{incident_id}/patch-verification", response_model=PatchVerificationResult)
def patch_verification(incident_id: str) -> PatchVerificationResult:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    execution = _latest_event_metadata(incident, "PATCH_EXECUTION")
    repository = str(execution.get("repository") or incident.incident.repo or "")
    commit_sha = execution.get("commit_sha")
    draft_pr_number = execution.get("draft_pr_number")
    if not repository or not commit_sha or not draft_pr_number:
        raise HTTPException(
            status_code=409,
            detail="No executed remediation with a draft PR is available for CI verification.",
        )

    try:
        result = verify_patch_ci(
            incident,
            repository=repository,
            commit_sha=str(commit_sha),
            draft_pr_number=int(draft_pr_number),
        )
    except PatchVerificationUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    previous = _latest_event_metadata(incident, "PATCH_CI_VERIFICATION")
    changed = previous.get("status") != result.status or previous.get("commit_sha") != result.commit_sha
    if changed:
        store.append_event(
            incident_id,
            "PATCH_CI_VERIFICATION",
            result.message,
            {
                "status": result.status,
                "repository": result.repository,
                "commit_sha": result.commit_sha,
                "draft_pr_number": result.draft_pr_number,
                "draft_pr_url": result.draft_pr_url,
                "pr_state": result.pr_state,
                "pr_draft": result.pr_draft,
                "checks": [check.model_dump() for check in result.checks],
                "derived_incident_outcome": result.derived_incident_outcome.value if result.derived_incident_outcome else None,
                "verification_evidence": result.verification_evidence,
                "runtime_verification_required": result.runtime_verification_required,
            },
        )
        store.append_event(
            incident_id,
            "VERIFICATION_DERIVED",
            "Incident verification evidence was derived from the real remediation commit and GitHub CI state.",
            {
                "source": "github-ci",
                "ci_status": result.status,
                "derived_outcome": result.derived_incident_outcome.value if result.derived_incident_outcome else None,
                "evidence": result.verification_evidence,
                "runtime_verification_required": result.runtime_verification_required,
            },
        )

    store.set_status(incident_id, result.incident_status)
    return result


@router.post("/incidents/{incident_id}/patch-merge", response_model=PatchMergeResult)
def merge_patch(incident_id: str, payload: PatchMergeRequest) -> PatchMergeResult:
    """Second explicit human gate for an already validated remediation PR.

    This endpoint is never invoked by CI or background automation. It is only
    available after the operator explicitly confirms MERGE in the product UI.
    """
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    execution = _latest_event_metadata(incident, "PATCH_EXECUTION")
    repository = str(execution.get("repository") or incident.incident.repo or "")
    commit_sha = str(execution.get("commit_sha") or "")
    draft_pr_number = int(execution.get("draft_pr_number") or 0)
    if not repository or not commit_sha or not draft_pr_number:
        raise HTTPException(status_code=409, detail="No validated remediation Draft PR is available to merge.")

    previous = _existing_merge_result(incident, repository=repository, draft_pr_number=draft_pr_number)
    if previous is not None:
        return previous

    merge_lock_key = f"merge:{repository}:{draft_pr_number}:{commit_sha}"
    with _lock_for(merge_lock_key):
        refreshed = store.get(incident_id)
        if refreshed is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        previous = _existing_merge_result(refreshed, repository=repository, draft_pr_number=draft_pr_number)
        if previous is not None:
            return previous

        try:
            result = merge_verified_patch_pr(
                refreshed,
                repository=repository,
                commit_sha=commit_sha,
                draft_pr_number=draft_pr_number,
                reviewer=payload.reviewer,
                confirmation=payload.confirmation,
                merge_method=payload.merge_method,
            )
        except PatchMergeUnavailable as exc:
            store.append_event(
                incident_id,
                "PATCH_MERGE_BLOCKED",
                "Human-confirmed merge was blocked by a fresh safety check.",
                {
                    "repository": repository,
                    "draft_pr_number": draft_pr_number,
                    "commit_sha": commit_sha,
                    "reviewer": payload.reviewer,
                    "reason": str(exc),
                },
            )
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        store.append_event(
            incident_id,
            "PATCH_MERGED",
            result.message,
            {
                "repository": result.repository,
                "draft_pr_number": result.draft_pr_number,
                "merge_sha": result.merge_sha,
                "merge_method": result.merge_method,
                "reviewer": result.reviewer,
                "runtime_verification_required": result.runtime_verification_required,
            },
        )
        store.append_event(
            incident_id,
            "RUNTIME_VERIFICATION_REQUIRED",
            "Repository merge completed, but the original runtime incident still requires independent verification.",
            {
                "source": "human-confirmed-merge",
                "merge_sha": result.merge_sha,
                "draft_pr_number": result.draft_pr_number,
            },
        )
        store.set_status(incident_id, IncidentStatus.verifying)
        return result

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.repositories.incidents import IncidentStore
from app.schemas.incident import ApprovalDecision, IncidentStatus, PatchProposalRequest
from app.schemas.patch import PatchDecisionRequest, PatchExecutionResult
from app.services.github_context import GitHubContextUnavailable, collect_repository_context
from app.services.patch_execution import execute_approved_patch
from app.services.patch_proposal import PatchProposalUnavailable, build_patch_proposal

router = APIRouter(prefix="/api/v1", tags=["patch-remediation"])
store = IncidentStore.from_env()


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
            {"proposal_id": payload.proposal.proposal_id, "reason": str(exc)},
        )
        raise HTTPException(status_code=409, detail=f"Reviewed patch is stale or unavailable: {exc}") from exc

    if not _same_exact_proposal(fresh, payload.proposal):
        store.append_event(
            incident_id,
            "PATCH_STALE",
            "Patch approval blocked because the live proposal changed since review.",
            {"proposal_id": payload.proposal.proposal_id, "fresh_proposal_id": fresh.proposal_id},
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
            "branch": result.branch,
            "commit_sha": result.commit_sha,
            "draft_pr_number": result.draft_pr_number,
            "draft_pr_url": result.draft_pr_url,
            "validation": [check.model_dump() for check in result.validation],
        },
    )
    store.set_status(incident_id, result.incident_status)
    return result

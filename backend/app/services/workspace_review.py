from __future__ import annotations

from pathlib import Path

from app.schemas.workspace import WorkspaceFixProposal, WorkspaceFixResult
from app.services.workspace_autofix import _apply_candidate, get_target, scan_target


def apply_reviewed_proposal(target_id: str, reviewed: WorkspaceFixProposal) -> WorkspaceFixResult:
    """Apply only the exact workspace patch that was previously presented for review.

    This deliberately does not regenerate or substitute an AI/deterministic proposal at write time.
    If the workspace changed after review, the underlying exact-before check fails closed. If real
    validation fails, the original source is restored and the operator must preview a new proposal.
    """

    target = get_target(target_id)
    if reviewed.target_id != target_id:
        raise ValueError("Reviewed proposal belongs to a different workspace target")
    if reviewed.writes_files:
        raise ValueError("Reviewed proposal must be a no-write preview")
    if reviewed.strategy == "NONE" or not reviewed.file_path or not reviewed.after:
        raise ValueError("Reviewed proposal contains no executable bounded repair")

    before_scan = scan_target(target_id)
    if before_scan.verification.passed:
        raise ValueError("Reviewed proposal is stale; workspace is already healthy")
    if before_scan.diagnosis.status != "BUG_CONFIRMED":
        raise ValueError("Reviewed proposal is stale; the current bug is no longer safely confirmed")
    if before_scan.diagnosis.file_path != reviewed.file_path:
        raise ValueError("Reviewed proposal is stale; the diagnosed file changed")

    audit = [
        "Workspace path containment verified.",
        "Operator approval is bound to the exact previously previewed proposal.",
        f"Pre-fix validator exited with {before_scan.verification.exit_code}.",
        f"Diagnosis status: {before_scan.diagnosis.status}.",
        f"Reviewed planner: {reviewed.strategy} via {reviewed.reasoning_provider}/{reviewed.reasoning_model}.",
    ]
    if reviewed.fallback_reason:
        audit.append(reviewed.fallback_reason)

    target_root = Path(before_scan.workspace_path)
    audit.append(f"Applying exact reviewed edit to {reviewed.file_path}.")
    after_verification, rolled_back = _apply_candidate(target_root, reviewed)
    audit.append(f"Post-fix validator exited with {after_verification.exit_code}.")

    if after_verification.passed:
        audit.append("The same real validator now passes; the reviewed repair is proven for the tested regression.")
        return WorkspaceFixResult(
            target=target,
            before_verification=before_scan.verification,
            diagnosis=before_scan.diagnosis,
            proposal=reviewed.model_copy(update={"writes_files": True}),
            applied=True,
            rolled_back=False,
            after_verification=after_verification,
            final_status="FIXED",
            audit=audit,
        )

    audit.append("Reviewed repair failed validation; original source was restored and no substitute patch was auto-applied.")
    return WorkspaceFixResult(
        target=target,
        before_verification=before_scan.verification,
        diagnosis=before_scan.diagnosis,
        proposal=reviewed.model_copy(update={"writes_files": True}),
        applied=True,
        rolled_back=rolled_back,
        after_verification=after_verification,
        final_status="ROLLED_BACK",
        audit=audit,
    )

from __future__ import annotations

import httpx

from app.schemas.incident import IncidentRecord, IncidentStatus
from app.schemas.patch import PatchMergeResult
from app.services.github_client import (
    GITHUB_API,
    github_headers,
    github_token,
    github_write_readiness,
    normalize_repo,
    repository_allowed,
)
from app.services.patch_verification import PatchVerificationUnavailable, verify_patch_ci


class PatchMergeUnavailable(RuntimeError):
    pass


def _require_merge_confirmation(confirmation: str) -> None:
    if confirmation.strip().upper() != "MERGE":
        raise PatchMergeUnavailable("Final merge confirmation must be exactly MERGE.")


def _require_matching_open_pr(pr: dict, *, expected_commit_sha: str) -> None:
    if str(pr.get("state") or "").lower() != "open":
        raise PatchMergeUnavailable("The pull request is no longer open.")

    head = pr.get("head") if isinstance(pr, dict) else None
    head_sha = str(head.get("sha") or "") if isinstance(head, dict) else ""
    if not head_sha or head_sha != expected_commit_sha:
        raise PatchMergeUnavailable("The pull request head changed after remediation review. Refresh evidence before merging.")


def _json_or_error(response: httpx.Response, action: str) -> dict:
    if response.status_code >= 400:
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("message") or "")[:260]
        except ValueError:
            detail = response.text[:260]
        raise PatchMergeUnavailable(f"GitHub {action} failed with HTTP {response.status_code}: {detail or 'request failed'}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise PatchMergeUnavailable(f"GitHub returned a non-JSON response while attempting to {action}.") from exc
    if not isinstance(payload, dict):
        raise PatchMergeUnavailable(f"GitHub returned an unexpected response while attempting to {action}.")
    return payload


def _mark_ready_for_review(client: httpx.Client, *, node_id: str) -> None:
    mutation = """
    mutation MarkReady($id: ID!) {
      markPullRequestReadyForReview(input: {pullRequestId: $id}) {
        pullRequest { id isDraft }
      }
    }
    """
    response = client.post(
        "https://api.github.com/graphql",
        json={"query": mutation, "variables": {"id": node_id}},
    )
    payload = _json_or_error(response, "mark the Draft PR ready for review")
    if payload.get("errors"):
        message = str(payload.get("errors"))[:320]
        raise PatchMergeUnavailable(f"GitHub refused to mark the Draft PR ready for review: {message}")


def merge_verified_patch_pr(
    incident: IncidentRecord,
    *,
    repository: str,
    commit_sha: str,
    draft_pr_number: int,
    reviewer: str,
    confirmation: str,
    merge_method: str = "squash",
) -> PatchMergeResult:
    """Merge one exact remediation PR only after a second explicit human action.

    This is intentionally not auto-merge: CI PASS alone never invokes this function.
    The caller must provide the final MERGE confirmation after reviewing the PR.
    Production/runtime verification still remains separate after repository merge.
    """
    _require_merge_confirmation(confirmation)

    normalized_repo = normalize_repo(repository)
    if not normalized_repo or not repository_allowed(normalized_repo):
        raise PatchMergeUnavailable("Repository is not in the configured GitHub write allowlist.")

    readiness = github_write_readiness(normalized_repo)
    if not readiness.get("write_access"):
        raise PatchMergeUnavailable(str(readiness.get("reason") or "GitHub write permission is unavailable."))

    token = github_token()
    if not token:
        raise PatchMergeUnavailable("No authenticated GitHub write credential is available.")

    try:
        verification = verify_patch_ci(
            incident,
            repository=normalized_repo,
            commit_sha=commit_sha,
            draft_pr_number=draft_pr_number,
        )
    except PatchVerificationUnavailable as exc:
        raise PatchMergeUnavailable(f"CI verification could not be refreshed before merge: {exc}") from exc

    if verification.status != "PASS":
        raise PatchMergeUnavailable(f"Merge is locked until real GitHub CI reports PASS; current status is {verification.status}.")

    headers = github_headers(token=token)
    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        try:
            pr_response = client.get(f"{GITHUB_API}/repos/{normalized_repo}/pulls/{draft_pr_number}")
        except httpx.HTTPError as exc:
            raise PatchMergeUnavailable(f"GitHub PR revalidation failed: {type(exc).__name__}") from exc
        pr = _json_or_error(pr_response, "revalidate the pull request")
        _require_matching_open_pr(pr, expected_commit_sha=commit_sha)

        if bool(pr.get("draft", False)):
            node_id = str(pr.get("node_id") or "")
            if not node_id:
                raise PatchMergeUnavailable("Draft PR is missing its GitHub node id; merge stopped before any merge write.")
            _mark_ready_for_review(client, node_id=node_id)

        try:
            merge_response = client.put(
                f"{GITHUB_API}/repos/{normalized_repo}/pulls/{draft_pr_number}/merge",
                json={
                    "sha": commit_sha,
                    "merge_method": merge_method,
                    "commit_title": f"Verified incident remediation #{draft_pr_number}",
                },
            )
        except httpx.HTTPError as exc:
            raise PatchMergeUnavailable(f"GitHub merge request failed: {type(exc).__name__}") from exc
        merged_payload = _json_or_error(merge_response, "merge the pull request")

    if not bool(merged_payload.get("merged", False)):
        message = str(merged_payload.get("message") or "GitHub did not merge the pull request.")
        raise PatchMergeUnavailable(message[:320])

    return PatchMergeResult(
        incident_id=incident.id,
        repository=normalized_repo,
        draft_pr_number=draft_pr_number,
        merged=True,
        merge_sha=str(merged_payload.get("sha") or "") or None,
        merge_method=merge_method,
        reviewer=reviewer,
        message=(
            "The human-confirmed remediation pull request was merged after fresh CI and head-SHA revalidation. "
            "Production recovery is still not assumed; runtime verification remains required."
        ),
        incident_status=IncidentStatus.verifying,
        runtime_verification_required=True,
    )

from __future__ import annotations

from typing import Any

import httpx

from app.schemas.incident import IncidentRecord, IncidentStatus, VerificationOutcome
from app.schemas.patch import CIVerificationCheck, PatchVerificationResult
from app.services.github_client import GITHUB_API, github_headers, github_token, normalize_repo, repository_allowed


class PatchVerificationUnavailable(RuntimeError):
    pass


_FAIL_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"}
_PASS_CONCLUSIONS = {"success", "neutral", "skipped"}


def _request(client: httpx.Client, path: str) -> Any:
    try:
        response = client.get(path)
    except httpx.HTTPError as exc:
        raise PatchVerificationUnavailable(f"GitHub verification request failed: {type(exc).__name__}") from exc
    if response.status_code >= 400:
        detail = ""
        try:
            detail = str(response.json().get("message", ""))[:240]
        except ValueError:
            detail = response.text[:240]
        raise PatchVerificationUnavailable(
            f"GitHub returned {response.status_code} while reading verification state: {detail or 'request failed'}"
        )
    try:
        return response.json()
    except ValueError as exc:
        raise PatchVerificationUnavailable("GitHub returned a non-JSON verification response.") from exc


def _derive_status(checks: list[CIVerificationCheck], combined_state: str) -> tuple[str, str]:
    normalized_state = (combined_state or "").lower()
    conclusions = {(check.conclusion or "").lower() for check in checks if check.conclusion}
    statuses = {check.status.lower() for check in checks}

    if conclusions & _FAIL_CONCLUSIONS or normalized_state in {"failure", "error"}:
        return "FAIL", "At least one real GitHub CI/check result failed. The incident requires further remediation."

    if any(status in {"queued", "in_progress", "pending", "requested", "waiting"} for status in statuses):
        return "PENDING", "GitHub CI is still running for the isolated remediation commit."

    if normalized_state == "pending":
        return "PENDING", "GitHub commit status is still pending for the isolated remediation commit."

    if checks:
        # A green combined status must not mask an incomplete/ambiguous check-run. GitHub normally
        # supplies a conclusion for completed checks, but fail closed if a provider returns a
        # completed check without one or an unfamiliar non-terminal status.
        if any(check.status.lower() != "completed" for check in checks):
            return "PENDING", "At least one GitHub check has not reached a recognized terminal state yet."
        if any(not check.conclusion for check in checks):
            return "PENDING", "At least one completed GitHub check has no terminal conclusion yet."
        if conclusions.issubset(_PASS_CONCLUSIONS):
            return "PASS", "All observed GitHub checks completed without a failing conclusion. Human review is still required before merge."
        return "PENDING", "At least one GitHub check returned an unrecognized conclusion; verification fails closed until it is understood."

    if normalized_state == "success":
        return "PASS", "GitHub commit status reports success. Human review is still required before merge."

    if normalized_state in {"", "pending"}:
        return "NO_CHECKS", "No completed GitHub CI/check results are available yet for this remediation commit."

    return "PENDING", "GitHub verification state is not final yet."


def _derive_incident_verification(
    *,
    status: str,
    repository: str,
    commit_sha: str,
    draft_pr_number: int,
    checks: list[CIVerificationCheck],
) -> tuple[VerificationOutcome | None, str, bool]:
    observed = []
    for check in checks:
        terminal = check.conclusion or check.status
        observed.append(f"{check.name}={terminal}")
    check_summary = ", ".join(observed) if observed else "no check-runs observed"
    evidence = (
        f"GitHub remediation verification for {repository}@{commit_sha[:12]} on Draft PR #{draft_pr_number}: "
        f"CI={status}; {check_summary}."
    )

    if status == "FAIL":
        return VerificationOutcome.failed, evidence, False
    if status in {"PENDING", "NO_CHECKS"}:
        return VerificationOutcome.inconclusive, evidence, True

    # Passing CI is necessary evidence that the isolated remediation branch is green,
    # but it does not prove the original production/runtime symptom recovered.
    return None, evidence, True


def verify_patch_ci(
    incident: IncidentRecord,
    *,
    repository: str,
    commit_sha: str,
    draft_pr_number: int,
) -> PatchVerificationResult:
    normalized_repo = normalize_repo(repository)
    if not normalized_repo or not repository_allowed(normalized_repo):
        raise PatchVerificationUnavailable("Repository is not in the configured GitHub allowlist.")

    token = github_token()
    headers = github_headers(token=token)
    headers["Accept"] = "application/vnd.github+json"

    with httpx.Client(base_url=GITHUB_API, headers=headers, timeout=20.0, follow_redirects=True) as client:
        pr = _request(client, f"/repos/{normalized_repo}/pulls/{draft_pr_number}")
        check_payload = _request(client, f"/repos/{normalized_repo}/commits/{commit_sha}/check-runs")
        status_payload = _request(client, f"/repos/{normalized_repo}/commits/{commit_sha}/status")

    checks = [
        CIVerificationCheck(
            name=str(item.get("name") or "GitHub check"),
            status=str(item.get("status") or "unknown"),
            conclusion=item.get("conclusion"),
            details_url=item.get("details_url") or item.get("html_url"),
        )
        for item in check_payload.get("check_runs", [])
    ]

    status, message = _derive_status(checks, str(status_payload.get("state") or ""))
    derived_outcome, verification_evidence, runtime_required = _derive_incident_verification(
        status=status,
        repository=normalized_repo,
        commit_sha=commit_sha,
        draft_pr_number=draft_pr_number,
        checks=checks,
    )
    if status == "FAIL":
        incident_status = IncidentStatus.escalated
    else:
        incident_status = IncidentStatus.verifying

    return PatchVerificationResult(
        incident_id=incident.id,
        repository=normalized_repo,
        commit_sha=commit_sha,
        draft_pr_number=draft_pr_number,
        draft_pr_url=pr.get("html_url"),
        pr_state=str(pr.get("state") or "unknown").upper(),
        pr_draft=bool(pr.get("draft", False)),
        status=status,
        message=message,
        checks=checks,
        incident_status=incident_status,
        derived_incident_outcome=derived_outcome,
        verification_evidence=verification_evidence,
        runtime_verification_required=runtime_required,
    )

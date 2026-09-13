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
_RETRYABLE_GITHUB_READ_STATUSES = {502, 503, 504}
_GITHUB_READ_ATTEMPTS = 3
_CHECK_RUN_PAGE_SIZE = 100


def _request(client: httpx.Client, path: str) -> Any:
    """Read GitHub verification state with bounded retries for transient read failures only.

    This helper is deliberately scoped to idempotent GET requests. Repository writes are never
    retried here, and authentication/authorization/rate-limit failures still fail immediately.
    """
    last_transport_error: httpx.HTTPError | None = None
    for attempt in range(1, _GITHUB_READ_ATTEMPTS + 1):
        try:
            response = client.get(path)
        except httpx.HTTPError as exc:
            last_transport_error = exc
            if attempt < _GITHUB_READ_ATTEMPTS:
                continue
            raise PatchVerificationUnavailable(f"GitHub verification request failed: {type(exc).__name__}") from exc

        if response.status_code in _RETRYABLE_GITHUB_READ_STATUSES and attempt < _GITHUB_READ_ATTEMPTS:
            continue
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

    if last_transport_error is not None:
        raise PatchVerificationUnavailable(
            f"GitHub verification request failed: {type(last_transport_error).__name__}"
        ) from last_transport_error
    raise PatchVerificationUnavailable("GitHub verification request failed after bounded retries.")


def _read_all_check_runs(client: httpx.Client, repository: str, commit_sha: str) -> list[dict[str, Any]]:
    """Read the complete GitHub check-run set so a later page cannot hide a failure.

    GitHub paginates check runs. Treat inconsistent pagination metadata as unavailable rather than
    deriving PASS from a partial page.
    """
    first = _request(
        client,
        f"/repos/{repository}/commits/{commit_sha}/check-runs?per_page={_CHECK_RUN_PAGE_SIZE}&page=1",
    )
    first_runs = first.get("check_runs")
    if not isinstance(first_runs, list):
        raise PatchVerificationUnavailable("GitHub returned an invalid check-run payload during verification.")

    raw_total = first.get("total_count", len(first_runs))
    try:
        total_count = int(raw_total)
    except (TypeError, ValueError) as exc:
        raise PatchVerificationUnavailable("GitHub returned an invalid check-run total during verification.") from exc
    if total_count < 0:
        raise PatchVerificationUnavailable("GitHub returned an invalid check-run total during verification.")

    runs = list(first_runs)
    page = 2
    while len(runs) < total_count:
        payload = _request(
            client,
            f"/repos/{repository}/commits/{commit_sha}/check-runs?per_page={_CHECK_RUN_PAGE_SIZE}&page={page}",
        )
        page_runs = payload.get("check_runs")
        if not isinstance(page_runs, list) or not page_runs:
            raise PatchVerificationUnavailable(
                "GitHub check-run pagination was incomplete; refusing to derive CI verification from partial evidence."
            )
        runs.extend(page_runs)
        page += 1

    if len(runs) != total_count:
        raise PatchVerificationUnavailable(
            "GitHub check-run pagination changed during verification; refresh before trusting CI evidence."
        )
    return runs


def _validate_pr_binding(pr: dict[str, Any], *, commit_sha: str, draft_pr_number: int) -> None:
    observed_number = pr.get("number")
    if observed_number is not None:
        try:
            if int(observed_number) != draft_pr_number:
                raise PatchVerificationUnavailable(
                    f"GitHub returned PR #{observed_number} while verification expected Draft PR #{draft_pr_number}."
                )
        except (TypeError, ValueError) as exc:
            raise PatchVerificationUnavailable("GitHub returned an invalid pull-request number during verification.") from exc

    pr_state = str(pr.get("state") or "").lower()
    if pr_state != "open":
        raise PatchVerificationUnavailable(
            "The remediation pull request is no longer open. Refresh remediation state before trusting CI evidence."
        )

    if pr.get("draft") is not True:
        raise PatchVerificationUnavailable(
            "The remediation pull request is no longer a Draft PR. Human review state changed, so CI evidence must not be trusted automatically."
        )

    head = pr.get("head")
    if not isinstance(head, dict):
        raise PatchVerificationUnavailable("GitHub did not return the Draft PR head needed for verification.")

    head_ref = str(head.get("ref") or "")
    if not head_ref.startswith("incident-fix/"):
        raise PatchVerificationUnavailable(
            "The Draft PR no longer points at an isolated incident-fix remediation branch. Refresh remediation state before trusting CI evidence."
        )

    head_repo = head.get("repo")
    base = pr.get("base")
    base_repo = base.get("repo") if isinstance(base, dict) else None
    head_repo_name = str(head_repo.get("full_name") or "") if isinstance(head_repo, dict) else ""
    base_repo_name = str(base_repo.get("full_name") or "") if isinstance(base_repo, dict) else ""
    if head_repo_name and base_repo_name and head_repo_name.lower() != base_repo_name.lower():
        raise PatchVerificationUnavailable(
            "The remediation Draft PR now originates from a different repository. Cross-repository CI evidence is not trusted automatically."
        )

    head_sha = str(head.get("sha") or "")
    if not head_sha:
        raise PatchVerificationUnavailable("GitHub did not return the Draft PR head commit needed for verification.")
    if head_sha.lower() != commit_sha.lower():
        raise PatchVerificationUnavailable(
            "Draft PR head changed after the recorded remediation execution. Refresh remediation state before trusting CI evidence."
        )


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
        if any(check.status.lower() != "completed" for check in checks):
            return "PENDING", "At least one GitHub check has not reached a recognized terminal state yet."
        if any(not check.conclusion for check in checks):
            return "PENDING", "At least one completed GitHub check has no terminal conclusion yet."
        if conclusions.issubset(_PASS_CONCLUSIONS):
            if "success" in conclusions or normalized_state == "success":
                return "PASS", "All observed GitHub checks completed without a failing conclusion. Human review is still required before merge."
            return "PENDING", (
                "GitHub checks are only neutral/skipped and no successful commit status is available; "
                "verification fails closed until at least one real success signal exists."
            )
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
        _validate_pr_binding(pr, commit_sha=commit_sha, draft_pr_number=draft_pr_number)
        check_runs = _read_all_check_runs(client, normalized_repo, commit_sha)
        status_payload = _request(client, f"/repos/{normalized_repo}/commits/{commit_sha}/status")

    checks = [
        CIVerificationCheck(
            name=str(item.get("name") or "GitHub check"),
            status=str(item.get("status") or "unknown"),
            conclusion=item.get("conclusion"),
            details_url=item.get("details_url") or item.get("html_url"),
        )
        for item in check_runs
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

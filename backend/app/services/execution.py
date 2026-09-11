from __future__ import annotations

import os
from uuid import uuid4

import httpx

from app.schemas.incident import ActionExecutionResult, IncidentRecord, ProposedAction
from app.services.github_client import (
    GITHUB_API,
    configured_repository,
    github_headers,
    github_token,
    normalize_repo,
    repository_allowed,
)


def _demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "false").strip().lower() not in {"0", "false", "no", "off"}


def _github_token() -> str | None:
    """Backward-compatible wrapper used by tests and the live GitHub adapter."""
    return github_token()


def _latest_event_metadata(incident: IncidentRecord, stage: str) -> dict:
    for event in reversed(incident.timeline):
        if event.stage == stage:
            return event.metadata
    return {}


def _issue_payload(incident: IncidentRecord, action: ProposedAction) -> tuple[str, str]:
    rca = _latest_event_metadata(incident, "RCA")
    remediation = _latest_event_metadata(incident, "REMEDIATION")
    repository_evidence = _latest_event_metadata(incident, "REPOSITORY_EVIDENCE")

    title = f"[Incident {incident.id}] {incident.incident.title}"[:240]
    body = "\n".join(
        [
            "## Incident",
            f"- **ID:** `{incident.id}`",
            f"- **Environment:** `{incident.incident.environment}`",
            f"- **Component:** `{incident.triage.component}`",
            f"- **Severity:** `{incident.triage.severity.value}`",
            f"- **Owner:** `{incident.triage.owner_team}`",
            f"- **Triage confidence:** `{incident.triage.confidence:.0%}`",
            f"- **Repository:** `{incident.incident.repo or action.target}`",
            "",
            "### Report",
            incident.incident.description,
            "",
            "## Evidence-backed RCA",
            f"**Working hypothesis:** {rca.get('title', 'Not recorded')}",
            f"**Confidence:** {rca.get('confidence', 'Not recorded')}",
            "",
            "## Live repository evidence",
            f"**Top correlated commit:** {repository_evidence.get('top_commit', 'No correlated commit recorded')}",
            f"**Correlation:** {repository_evidence.get('top_correlation', 'Not available')}",
            f"**Changed files:** {', '.join(repository_evidence.get('changed_files', [])) or 'Not available'}",
            "",
            "## Approved remediation",
            remediation.get("summary", action.description),
            "",
            "## Verification plan",
            remediation.get("verification", "Repeat the original failing workflow and confirm expected behavior is restored."),
            "",
            "## Approved bounded action",
            action.description,
            "",
            "---",
            "Created by Kurukshetra Incident Command only after explicit human approval.",
        ]
    )
    return title, body


def _create_github_issue(incident: IncidentRecord, action: ProposedAction) -> ActionExecutionResult:
    action_id = f"ACT-{uuid4().hex[:10].upper()}"
    configured_repo = configured_repository()
    requested_repo = normalize_repo(action.target or configured_repo)

    if not repository_allowed(requested_repo):
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident.id,
            action_type=action.action_type,
            target=requested_repo,
            status="BLOCKED",
            mode="POLICY",
            message="GitHub action blocked because the target repository is outside the configured allowlist.",
        )

    token = _github_token()
    if not token:
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident.id,
            action_type=action.action_type,
            target=requested_repo,
            status="AUTH_REQUIRED",
            mode="LIVE",
            message="GitHub issue was not created because live GitHub authentication is not configured.",
        )

    title, body = _issue_payload(incident, action)
    try:
        response = httpx.post(
            f"{GITHUB_API}/repos/{requested_repo}/issues",
            headers=github_headers(token=token),
            json={"title": title, "body": body},
            timeout=12.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident.id,
            action_type=action.action_type,
            target=requested_repo,
            status="FAILED",
            mode="GITHUB",
            message=f"GitHub issue creation failed safely: {type(exc).__name__}.",
        )

    external_url = payload.get("html_url")
    issue_number = payload.get("number")
    return ActionExecutionResult(
        action_id=action_id,
        incident_id=incident.id,
        action_type=action.action_type,
        target=requested_repo,
        status="EXECUTED",
        mode="GITHUB",
        message=f"GitHub issue #{issue_number} created successfully: {external_url}",
        external_url=external_url,
    )


def execute_bounded_action(
    incident_id: str,
    action: ProposedAction,
    incident: IncidentRecord | None = None,
) -> ActionExecutionResult:
    """Execute explicitly bounded adapters only after policy and human-approval gates."""
    action_id = f"ACT-{uuid4().hex[:10].upper()}"

    if _demo_mode():
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident_id,
            action_type=action.action_type,
            target=action.target,
            status="SIMULATED",
            mode="DEMO",
            message="Emergency demo mode is enabled; no external system was modified.",
        )

    action_type = action.action_type.strip().lower()
    if action_type in {"create github issue", "github issue", "create issue"}:
        if incident is None:
            return ActionExecutionResult(
                action_id=action_id,
                incident_id=incident_id,
                action_type=action.action_type,
                target=action.target,
                status="FAILED",
                mode="GITHUB",
                message="GitHub issue creation requires the persisted incident context.",
            )
        return _create_github_issue(incident, action)

    return ActionExecutionResult(
        action_id=action_id,
        incident_id=incident_id,
        action_type=action.action_type,
        target=action.target,
        status="UNAVAILABLE",
        mode="LIVE",
        message="No live adapter is configured for this action type; nothing was executed.",
    )

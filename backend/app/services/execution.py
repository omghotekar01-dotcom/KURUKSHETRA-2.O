from __future__ import annotations

import os
import shutil
import subprocess
from uuid import uuid4

import httpx

from app.schemas.incident import ActionExecutionResult, IncidentRecord, ProposedAction


DEFAULT_REPOSITORY = "omghotekar01-dotcom/KURUKSHETRA-2.O"
GITHUB_API = "https://api.github.com"


def _demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "true").strip().lower() not in {"0", "false", "no", "off"}


def _github_token() -> str | None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token

    allow_cli = os.getenv("ALLOW_GH_CLI_AUTH", "true").strip().lower() not in {"0", "false", "no", "off"}
    if not allow_cli or shutil.which("gh") is None:
        return None

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    return result.stdout.strip() or None


def _normalize_repo(value: str) -> str:
    normalized = value.strip().removesuffix(".git").strip("/")
    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if normalized.lower().startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    return normalized.strip("/")


def _latest_event_metadata(incident: IncidentRecord, stage: str) -> dict:
    for event in reversed(incident.timeline):
        if event.stage == stage:
            return event.metadata
    return {}


def _issue_payload(incident: IncidentRecord, action: ProposedAction) -> tuple[str, str]:
    rca = _latest_event_metadata(incident, "RCA")
    remediation = _latest_event_metadata(incident, "REMEDIATION")

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
            "",
            "### Report",
            incident.incident.description,
            "",
            "## Evidence-backed RCA",
            f"**Working hypothesis:** {rca.get('title', 'Not recorded')} ",
            f"**Confidence:** {rca.get('confidence', 'Not recorded')}",
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
            "Created by the Kurukshetra Incident Command prototype only after explicit human approval.",
        ]
    )
    return title, body


def _create_github_issue(incident: IncidentRecord, action: ProposedAction) -> ActionExecutionResult:
    action_id = f"ACT-{uuid4().hex[:10].upper()}"
    configured_repo = _normalize_repo(os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    requested_repo = _normalize_repo(action.target or configured_repo)

    if requested_repo != configured_repo:
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident.id,
            action_type=action.action_type,
            target=requested_repo,
            status="BLOCKED",
            mode="POLICY",
            message=f"GitHub action blocked: target repository must be {configured_repo}.",
        )

    token = _github_token()
    if not token:
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident.id,
            action_type=action.action_type,
            target=requested_repo,
            status="PREPARED",
            mode="SAFE_PREVIEW",
            message="GitHub issue was not created because no GitHub authentication is configured.",
        )

    title, body = _issue_payload(incident, action)
    try:
        response = httpx.post(
            f"{GITHUB_API}/repos/{requested_repo}/issues",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "kurukshetra-incident-command",
            },
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
    """Execute only explicitly bounded adapters after the policy and human-approval gates."""
    action_id = f"ACT-{uuid4().hex[:10].upper()}"

    if _demo_mode():
        return ActionExecutionResult(
            action_id=action_id,
            incident_id=incident_id,
            action_type=action.action_type,
            target=action.target,
            status="SIMULATED",
            mode="DEMO",
            message="Action recorded in demo mode; no external system was modified.",
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
        status="PREPARED",
        mode="SAFE_PREVIEW",
        message="No live adapter is configured for this action type; the approved action remains a safe preview.",
    )

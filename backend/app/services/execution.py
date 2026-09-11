from __future__ import annotations

import os
from uuid import uuid4

from app.schemas.incident import ActionExecutionResult, ProposedAction


def _demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "true").strip().lower() not in {"0", "false", "no", "off"}


def execute_bounded_action(incident_id: str, action: ProposedAction) -> ActionExecutionResult:
    """Execute only the bounded demo adapter until a real integration is explicitly configured.

    The adapter intentionally records what would happen without pretending an external
    provider accepted the action. A real GitHub adapter can replace this behind the same
    response contract once credentials and a controlled repository are configured.
    """
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

    return ActionExecutionResult(
        action_id=action_id,
        incident_id=incident_id,
        action_type=action.action_type,
        target=action.target,
        status="PREPARED",
        mode="SAFE_PREVIEW",
        message="No live action adapter is configured; the approved action remains a safe preview.",
    )

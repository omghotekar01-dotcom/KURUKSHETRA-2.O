from __future__ import annotations

from app.schemas.incident import (
    AnalysisBundle,
    EvidenceBundle,
    IncidentRecord,
    ProposedAction,
    RemediationPlan,
    RootCauseHypothesis,
)
from app.services.retrieval import retrieve_runbooks
from app.services.risk import evaluate_action


NEXT_DIAGNOSTIC = {
    "Authentication": "Compare the runtime signing/auth configuration with the latest deployment configuration.",
    "Database": "Inspect connection saturation, query plan, and recent schema/configuration changes.",
    "Backend": "Check application worker health, upstream connectivity, and recent backend changes.",
    "Frontend": "Reproduce the regression at the affected viewport and compare the latest UI changes.",
    "Infrastructure": "Inspect workload events, health checks, resource pressure, and the latest rollout.",
}

VERIFICATION = {
    "Authentication": "Run an authenticated request and confirm the protected endpoint returns the expected success response.",
    "Database": "Repeat the failing database-backed request and confirm latency/errors return to the expected range.",
    "Backend": "Call the health endpoint through the normal proxy path and verify the failing API request succeeds.",
    "Frontend": "Reproduce the affected user flow at the failing viewport and verify the visual regression is gone.",
    "Infrastructure": "Confirm healthy replicas remain stable and the affected service passes its health checks.",
}


def analyze_incident(record: IncidentRecord) -> AnalysisBundle:
    matches = retrieve_runbooks(record)
    evidence = EvidenceBundle(
        incident_id=record.id,
        matches=matches,
        no_strong_match=len(matches) == 0,
    )

    if not matches:
        return AnalysisBundle(
            incident_id=record.id,
            evidence=evidence,
            hypotheses=[],
            remediation=None,
            needs_human_investigation=True,
        )

    top = matches[0]
    supporting = matches[:2]
    confidence = min(0.92, round(0.48 + (top.score * 0.5), 2))
    hypothesis = RootCauseHypothesis(
        id="HYP-001",
        title=top.issue,
        confidence=confidence,
        evidence_ids=[match.id for match in supporting],
        rationale=(
            f"The strongest historical match is {top.id} ({top.score:.0%}) and it aligns "
            f"with the incident's {record.triage.component} triage signals."
        ),
        next_diagnostic=NEXT_DIAGNOSTIC.get(
            record.triage.component,
            "Collect one more direct diagnostic signal before taking a consequential action.",
        ),
    )

    action = ProposedAction(
        action_type="draft remediation plan",
        target=record.incident.repo or record.triage.owner_team,
        description=f"Prepare a bounded remediation using runbook {top.id}: {top.fix}",
        confidence=confidence,
        destructive=False,
    )
    risk = evaluate_action(action)
    remediation = RemediationPlan(
        summary=top.fix,
        steps=[
            "Confirm the top hypothesis with the next diagnostic check.",
            top.fix,
            "Run the defined verification before marking the incident resolved.",
        ],
        verification=VERIFICATION.get(
            record.triage.component,
            "Repeat the original failing workflow and confirm the expected behavior is restored.",
        ),
        proposed_action=action,
        risk=risk,
    )

    return AnalysisBundle(
        incident_id=record.id,
        evidence=evidence,
        hypotheses=[hypothesis],
        remediation=remediation,
        needs_human_investigation=False,
    )

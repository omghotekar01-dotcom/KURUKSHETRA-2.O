from __future__ import annotations

import os

from app.schemas.incident import (
    AnalysisBundle,
    EvidenceBundle,
    IncidentRecord,
    ProposedAction,
    RemediationPlan,
    ResolutionMemory,
    RootCauseHypothesis,
)
from app.services.retrieval import retrieve_knowledge
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


def analyze_incident(
    record: IncidentRecord,
    memories: list[ResolutionMemory] | None = None,
) -> AnalysisBundle:
    matches = retrieve_knowledge(record, memories=memories)
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
            f"The strongest knowledge match is {top.id} ({top.score:.0%}, source: {top.source}) "
            f"and it aligns with the incident's {record.triage.component} triage signals."
        ),
        next_diagnostic=NEXT_DIAGNOSTIC.get(
            record.triage.component,
            "Collect one more direct diagnostic signal before taking a consequential action.",
        ),
    )

    configured_repo = os.getenv("GITHUB_REPOSITORY", "omghotekar01-dotcom/KURUKSHETRA-2.O")
    action = ProposedAction(
        action_type="create github issue",
        target=record.incident.repo or configured_repo,
        description=(
            "Create a GitHub incident issue containing the evidence-backed RCA, approved remediation, "
            "and verification plan for human tracking."
        ),
        confidence=confidence,
        destructive=False,
    )
    risk = evaluate_action(action)
    remediation = RemediationPlan(
        summary=top.fix,
        steps=[
            "Confirm the top hypothesis with the next diagnostic check.",
            top.fix,
            "Create a tracked GitHub incident issue after explicit human approval.",
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

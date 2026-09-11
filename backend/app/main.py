from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.repositories.incidents import IncidentStore
from app.schemas.incident import (
    AnalysisBundle,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalResult,
    EvidenceBundle,
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    IncidentSummary,
    ProposedAction,
    RiskDecision,
    RiskLevel,
    TriageResult,
    VerificationOutcome,
    VerificationRequest,
    VerificationResult,
)
from app.services.analysis import analyze_incident
from app.services.execution import execute_bounded_action
from app.services.retrieval import retrieve_runbooks
from app.services.risk import evaluate_action
from app.services.triage import triage_incident

app = FastAPI(
    title="Kurukshetra Incident Command API",
    version="0.5.0",
    description="API-first foundation for evidence-backed, risk-aware incident response.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

incident_store = IncidentStore.from_env()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/api/v1/incidents/triage", response_model=TriageResult)
def triage(payload: IncidentIn) -> TriageResult:
    return triage_incident(payload)


@app.post("/api/v1/incidents", response_model=IncidentRecord, status_code=201)
def create_incident(payload: IncidentIn) -> IncidentRecord:
    triage_result = triage_incident(payload)
    return incident_store.create(payload, triage_result)


@app.get("/api/v1/incidents", response_model=list[IncidentSummary])
def list_incidents(limit: int = Query(default=50, ge=1, le=100)) -> list[IncidentSummary]:
    return incident_store.list(limit=limit)


@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentRecord)
def get_incident(incident_id: str) -> IncidentRecord:
    incident = incident_store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/api/v1/incidents/{incident_id}/investigate", response_model=EvidenceBundle)
def investigate_incident(incident_id: str) -> EvidenceBundle:
    incident = incident_store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    matches = retrieve_runbooks(incident)
    incident_store.append_event(
        incident_id,
        "EVIDENCE",
        f"Retrieved {len(matches)} relevant historical runbook match(es).",
        {"match_ids": [match.id for match in matches]},
    )
    return EvidenceBundle(
        incident_id=incident_id,
        matches=matches,
        no_strong_match=len(matches) == 0,
    )


@app.post("/api/v1/incidents/{incident_id}/analyze", response_model=AnalysisBundle)
def analyze_incident_endpoint(incident_id: str) -> AnalysisBundle:
    incident = incident_store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    analysis = analyze_incident(incident)
    if analysis.needs_human_investigation:
        incident_store.set_status(incident_id, IncidentStatus.escalated)
        incident_store.append_event(
            incident_id,
            "RCA",
            "No strong historical match; escalated for human investigation.",
            {},
        )
        return analysis

    hypothesis = analysis.hypotheses[0]
    incident_store.append_event(
        incident_id,
        "RCA",
        f"Top root-cause hypothesis prepared at {hypothesis.confidence:.0%} confidence.",
        {"hypothesis_id": hypothesis.id, "evidence_ids": hypothesis.evidence_ids},
    )
    incident_store.set_status(incident_id, IncidentStatus.remediation_ready)
    incident_store.append_event(
        incident_id,
        "REMEDIATION",
        "Remediation and verification plan prepared for review.",
        {"risk": analysis.remediation.risk.risk.value if analysis.remediation and analysis.remediation.risk else None},
    )
    return analysis


@app.post("/api/v1/incidents/{incident_id}/approval", response_model=ApprovalResult)
def decide_action(incident_id: str, payload: ApprovalRequest) -> ApprovalResult:
    incident = incident_store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status not in {IncidentStatus.remediation_ready, IncidentStatus.awaiting_approval}:
        raise HTTPException(status_code=409, detail=f"Incident is not awaiting an action decision ({incident.status.value}).")

    risk = evaluate_action(payload.action)
    incident_store.append_event(
        incident_id,
        "APPROVAL",
        f"{payload.decision.value} recorded by {payload.reviewer}.",
        {
            "reviewer": payload.reviewer,
            "note": payload.note,
            "action_type": payload.action.action_type,
            "target": payload.action.target,
            "risk": risk.risk.value,
            "policy": risk.policy,
        },
    )

    if payload.decision is ApprovalDecision.reject:
        incident_store.set_status(incident_id, IncidentStatus.escalated)
        return ApprovalResult(
            incident_id=incident_id,
            decision=payload.decision,
            risk=risk,
            execution=None,
            incident_status=IncidentStatus.escalated,
        )

    if risk.risk is RiskLevel.high or risk.policy == "RECOMMENDATION_ONLY":
        incident_store.append_event(
            incident_id,
            "ACTION_BLOCKED",
            "High-risk action was not executed; external production-grade authorization is required.",
            {"risk": risk.risk.value, "policy": risk.policy},
        )
        incident_store.set_status(incident_id, IncidentStatus.escalated)
        return ApprovalResult(
            incident_id=incident_id,
            decision=payload.decision,
            risk=risk,
            execution=None,
            incident_status=IncidentStatus.escalated,
        )

    incident_store.set_status(incident_id, IncidentStatus.executing)
    execution = execute_bounded_action(incident_id, payload.action)
    incident_store.append_event(
        incident_id,
        "ACTION",
        execution.message,
        {
            "action_id": execution.action_id,
            "action_type": execution.action_type,
            "target": execution.target,
            "status": execution.status,
            "mode": execution.mode,
        },
    )
    incident_store.set_status(incident_id, IncidentStatus.verifying)
    return ApprovalResult(
        incident_id=incident_id,
        decision=payload.decision,
        risk=risk,
        execution=execution,
        incident_status=IncidentStatus.verifying,
    )


@app.post("/api/v1/incidents/{incident_id}/verify", response_model=VerificationResult)
def verify_incident(incident_id: str, payload: VerificationRequest) -> VerificationResult:
    incident = incident_store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status is not IncidentStatus.verifying:
        raise HTTPException(status_code=409, detail=f"Incident is not ready for verification ({incident.status.value}).")

    if payload.outcome is VerificationOutcome.passed:
        final_status = IncidentStatus.resolved
        message = "Verification passed; incident marked resolved."
    elif payload.outcome is VerificationOutcome.failed:
        final_status = IncidentStatus.escalated
        message = "Verification failed; incident escalated for further investigation."
    else:
        final_status = IncidentStatus.escalated
        message = "Verification was inconclusive; incident escalated for further investigation."

    incident_store.append_event(
        incident_id,
        "VERIFICATION",
        message,
        {
            "outcome": payload.outcome.value,
            "evidence": payload.evidence,
            "checked_by": payload.checked_by,
        },
    )
    incident_store.set_status(incident_id, final_status)
    return VerificationResult(
        incident_id=incident_id,
        outcome=payload.outcome,
        incident_status=final_status,
        message=message,
    )


@app.post("/api/v1/actions/risk", response_model=RiskDecision)
def action_risk(payload: ProposedAction) -> RiskDecision:
    return evaluate_action(payload)

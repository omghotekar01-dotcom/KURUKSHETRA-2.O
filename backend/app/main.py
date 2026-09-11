from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.repositories.incidents import IncidentStore
from app.schemas.incident import (
    AnalysisBundle,
    EvidenceBundle,
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    IncidentSummary,
    ProposedAction,
    RiskDecision,
    TriageResult,
)
from app.services.analysis import analyze_incident
from app.services.retrieval import retrieve_runbooks
from app.services.risk import evaluate_action
from app.services.triage import triage_incident

app = FastAPI(
    title="Kurukshetra Incident Command API",
    version="0.4.0",
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


@app.post("/api/v1/actions/risk", response_model=RiskDecision)
def action_risk(payload: ProposedAction) -> RiskDecision:
    return evaluate_action(payload)

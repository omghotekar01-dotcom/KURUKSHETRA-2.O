from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.repositories.incidents import IncidentStore
from app.schemas.incident import (
    IncidentIn,
    IncidentRecord,
    IncidentSummary,
    ProposedAction,
    RiskDecision,
    TriageResult,
)
from app.services.risk import evaluate_action
from app.services.triage import triage_incident

app = FastAPI(
    title="Kurukshetra Incident Command API",
    version="0.2.0",
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


@app.post("/api/v1/actions/risk", response_model=RiskDecision)
def action_risk(payload: ProposedAction) -> RiskDecision:
    return evaluate_action(payload)

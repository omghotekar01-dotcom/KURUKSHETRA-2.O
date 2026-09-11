from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.incident import IncidentIn, ProposedAction, RiskDecision, TriageResult
from app.services.risk import evaluate_action
from app.services.triage import triage_incident

app = FastAPI(
    title="Kurukshetra Incident Command API",
    version="0.1.0",
    description="API-first foundation for evidence-backed, risk-aware incident response.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/api/v1/incidents/triage", response_model=TriageResult)
def triage(payload: IncidentIn) -> TriageResult:
    return triage_incident(payload)


@app.post("/api/v1/actions/risk", response_model=RiskDecision)
def action_risk(payload: ProposedAction) -> RiskDecision:
    return evaluate_action(payload)

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


class RiskLevel(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"


class IncidentStatus(str, Enum):
    new = "NEW"
    triaging = "TRIAGING"
    investigating = "INVESTIGATING"
    rca_ready = "RCA_READY"
    remediation_ready = "REMEDIATION_READY"
    awaiting_approval = "AWAITING_APPROVAL"
    executing = "EXECUTING"
    verifying = "VERIFYING"
    resolved = "RESOLVED"
    escalated = "ESCALATED"


class IncidentIn(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=10000)
    environment: str = Field(default="production", max_length=80)
    repo: Optional[str] = None
    logs: List[str] = Field(default_factory=list)


class TriageResult(BaseModel):
    component: str
    owner_team: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    signals: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    timestamp: datetime
    stage: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncidentRecord(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    status: IncidentStatus
    incident: IncidentIn
    triage: TriageResult
    timeline: List[TimelineEvent] = Field(default_factory=list)


class IncidentSummary(BaseModel):
    id: str
    title: str
    status: IncidentStatus
    severity: Severity
    component: str
    owner_team: str
    created_at: datetime
    updated_at: datetime


class KnowledgeMatch(BaseModel):
    id: str
    component: str
    issue: str
    fix: str
    source: str
    score: float = Field(ge=0.0, le=1.0)


class EvidenceBundle(BaseModel):
    incident_id: str
    matches: List[KnowledgeMatch] = Field(default_factory=list)
    no_strong_match: bool = False


class ProposedAction(BaseModel):
    action_type: str
    target: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    destructive: bool = False


class RiskDecision(BaseModel):
    risk: RiskLevel
    policy: str
    reason: str
    requires_human_approval: bool


class RootCauseHypothesis(BaseModel):
    id: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(default_factory=list)
    rationale: str
    next_diagnostic: str


class RemediationPlan(BaseModel):
    summary: str
    steps: List[str] = Field(default_factory=list)
    verification: str
    proposed_action: Optional[ProposedAction] = None
    risk: Optional[RiskDecision] = None


class AnalysisBundle(BaseModel):
    incident_id: str
    evidence: EvidenceBundle
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list)
    remediation: Optional[RemediationPlan] = None
    needs_human_investigation: bool = False

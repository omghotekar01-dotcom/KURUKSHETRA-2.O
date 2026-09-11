from enum import Enum
from typing import List, Optional

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

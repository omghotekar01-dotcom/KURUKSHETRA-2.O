from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.services.safety import sanitize_incident_text


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


class ApprovalDecision(str, Enum):
    approve = "APPROVE"
    reject = "REJECT"


class VerificationOutcome(str, Enum):
    passed = "PASS"
    failed = "FAIL"
    inconclusive = "INCONCLUSIVE"


class IncidentIn(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=10000)
    environment: str = Field(default="production", max_length=80)
    repo: Optional[str] = None
    logs: List[str] = Field(default_factory=list)

    @field_validator("title", "description", "environment", mode="before")
    @classmethod
    def redact_text_fields(cls, value: object) -> object:
        return sanitize_incident_text(value) if isinstance(value, str) else value

    @field_validator("logs", mode="before")
    @classmethod
    def redact_log_lines(cls, value: object) -> object:
        if isinstance(value, list):
            return [sanitize_incident_text(item) if isinstance(item, str) else item for item in value]
        return value


class DemoScenario(BaseModel):
    id: str = Field(min_length=3, max_length=80)
    name: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=1000)
    expected_component: str = Field(min_length=2, max_length=120)
    incident: IncidentIn


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


class RepositoryFileChange(BaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0


class RepositorySourceLine(BaseModel):
    line_number: int = Field(ge=1)
    content: str
    in_hunk: bool = False


class RepositoryDiffHunkEvidence(BaseModel):
    filename: str
    header: str
    added_lines: List[str] = Field(default_factory=list)
    removed_lines: List[str] = Field(default_factory=list)
    matched_terms: List[str] = Field(default_factory=list)
    source_context: List[RepositorySourceLine] = Field(default_factory=list)
    correlation_score: float = Field(default=0.0, ge=0.0, le=1.0)


class RepositoryCommitEvidence(BaseModel):
    sha: str
    short_sha: str
    message: str
    author: str
    authored_at: Optional[datetime] = None
    url: str
    files: List[RepositoryFileChange] = Field(default_factory=list)
    suspicious_hunks: List[RepositoryDiffHunkEvidence] = Field(default_factory=list)
    correlation_score: float = Field(default=0.0, ge=0.0, le=1.0)


class RepositoryIssueEvidence(BaseModel):
    number: int
    title: str
    state: str
    url: str
    labels: List[str] = Field(default_factory=list)


class RepositoryContext(BaseModel):
    repository: str
    default_branch: str
    fetched_at: datetime
    authenticated: bool
    source: str = "github-live"
    commits: List[RepositoryCommitEvidence] = Field(default_factory=list)
    open_issues: List[RepositoryIssueEvidence] = Field(default_factory=list)
    suggested_owners: List[str] = Field(default_factory=list)
    ownership_source: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class PatchProposalRequest(BaseModel):
    commit_sha: str = Field(min_length=7, max_length=64)
    filename: str = Field(min_length=1, max_length=500)
    hunk_header: str = Field(min_length=4, max_length=240)


class PatchProposal(BaseModel):
    proposal_id: str
    incident_id: str
    repository: str
    base_commit: str
    file_path: str
    hunk_header: str
    strategy: str = "REVERT_SUSPICIOUS_HUNK"
    line_start: int = Field(ge=1)
    before_lines: List[str] = Field(default_factory=list)
    after_lines: List[str] = Field(default_factory=list)
    diff_preview: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    verification_commands: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    writes_repository: bool = False


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
    repository_context: Optional[RepositoryContext] = None
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list)
    remediation: Optional[RemediationPlan] = None
    needs_human_investigation: bool = False


class ApprovalRequest(BaseModel):
    decision: ApprovalDecision
    action: ProposedAction
    reviewer: str = Field(default="human-reviewer", min_length=2, max_length=120)
    note: str = Field(default="", max_length=1000)


class ActionExecutionResult(BaseModel):
    action_id: str
    incident_id: str
    action_type: str
    target: str
    status: str
    mode: str
    message: str
    external_url: Optional[str] = None


class ApprovalResult(BaseModel):
    incident_id: str
    decision: ApprovalDecision
    risk: RiskDecision
    execution: Optional[ActionExecutionResult] = None
    incident_status: IncidentStatus


class VerificationRequest(BaseModel):
    outcome: VerificationOutcome
    evidence: str = Field(min_length=3, max_length=4000)
    checked_by: str = Field(default="verification-runner", min_length=2, max_length=120)


class VerificationResult(BaseModel):
    incident_id: str
    outcome: VerificationOutcome
    incident_status: IncidentStatus
    message: str


class ResolutionMemory(BaseModel):
    memory_id: str
    incident_id: str
    created_at: datetime
    component: str
    severity: Severity
    symptoms: str
    working_hypothesis: str
    remediation: str
    verification_evidence: str
    source: str = "verified-resolution"


class ResolutionMemoryList(BaseModel):
    items: List[ResolutionMemory] = Field(default_factory=list)

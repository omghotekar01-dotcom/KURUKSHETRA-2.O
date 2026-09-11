from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.incident import ApprovalDecision, IncidentStatus, PatchProposal


class PatchDecisionRequest(BaseModel):
    decision: ApprovalDecision
    proposal: PatchProposal
    reviewer: str = Field(default="human-reviewer", min_length=2, max_length=120)
    note: str = Field(default="", max_length=1000)


class ValidationCheck(BaseModel):
    name: str
    command: str
    status: str
    exit_code: Optional[int] = None
    output: str = ""


class PatchExecutionResult(BaseModel):
    incident_id: str
    proposal_id: str
    decision: ApprovalDecision
    status: str
    message: str
    repository: str
    branch: Optional[str] = None
    branch_url: Optional[str] = None
    commit_sha: Optional[str] = None
    draft_pr_number: Optional[int] = None
    draft_pr_url: Optional[str] = None
    validation: list[ValidationCheck] = Field(default_factory=list)
    incident_status: IncidentStatus


class CIVerificationCheck(BaseModel):
    name: str
    status: str
    conclusion: Optional[str] = None
    details_url: Optional[str] = None


class PatchVerificationResult(BaseModel):
    incident_id: str
    repository: str
    commit_sha: str
    draft_pr_number: int
    draft_pr_url: Optional[str] = None
    pr_state: str
    pr_draft: bool
    status: str
    message: str
    checks: list[CIVerificationCheck] = Field(default_factory=list)
    incident_status: IncidentStatus

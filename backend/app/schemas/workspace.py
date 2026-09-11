from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WorkspaceTarget(BaseModel):
    id: str
    name: str
    description: str
    relative_path: str
    problem: str
    proof: str
    validator: str


class CommandEvidence(BaseModel):
    command: str
    exit_code: int
    output: str
    passed: bool
    duration_ms: int


class WorkspaceFile(BaseModel):
    path: str
    size_bytes: int


class WorkspaceDiagnosis(BaseModel):
    target_id: str
    status: Literal["BUG_CONFIRMED", "HEALTHY", "UNRESOLVED"]
    summary: str
    file_path: str | None = None
    line_number: int | None = None
    evidence: list[str] = Field(default_factory=list)
    expected_value: str | None = None
    observed_value: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class WorkspaceScanResult(BaseModel):
    target: WorkspaceTarget
    workspace_path: str
    files: list[WorkspaceFile]
    verification: CommandEvidence
    diagnosis: WorkspaceDiagnosis
    safe_boundary: str


class WorkspaceFixProposal(BaseModel):
    target_id: str
    file_path: str
    summary: str
    before: str
    after: str
    diff: str
    confidence: float = Field(ge=0.0, le=1.0)
    writes_files: bool = False


class WorkspaceFixResult(BaseModel):
    target: WorkspaceTarget
    before_verification: CommandEvidence
    diagnosis: WorkspaceDiagnosis
    proposal: WorkspaceFixProposal
    applied: bool
    rolled_back: bool
    after_verification: CommandEvidence
    final_status: Literal["FIXED", "ROLLED_BACK", "ALREADY_HEALTHY", "UNRESOLVED"]
    audit: list[str] = Field(default_factory=list)


class ModelRuntimeStatus(BaseModel):
    mode: Literal["LOCAL_OLLAMA", "GEMINI_FREE", "DETERMINISTIC_FALLBACK"]
    provider: str
    model: str
    ready: bool
    endpoint: str | None = None
    note: str

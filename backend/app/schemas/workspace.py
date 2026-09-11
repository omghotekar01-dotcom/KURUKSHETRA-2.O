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
    strategy: Literal["AI_GROUNDED", "DETERMINISTIC_SAFE_RULE", "NONE"] = "NONE"
    reasoning_provider: str = "deterministic"
    reasoning_model: str = "evidence-rules-v1"
    fallback_reason: str | None = None


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


class ModelProbeResult(BaseModel):
    connected: bool
    provider: str
    model: str
    latency_ms: int
    reply: str
    note: str


class AdhocFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=240)
    content: str = Field(max_length=256_000)


class WorkspaceKnowledgeHit(BaseModel):
    id: str
    component: str
    issue: str
    fix: str
    source: str
    score: float = Field(ge=0.0, le=1.0)


class AdhocIntakeRequest(BaseModel):
    problem: str = Field(min_length=8, max_length=4_000)
    files: list[AdhocFileInput] = Field(min_length=1, max_length=12)
    trusted_test_execution: bool = False


class AdhocWorkspaceState(BaseModel):
    session_id: str
    problem: str
    files: list[WorkspaceFile]
    knowledge: list[WorkspaceKnowledgeHit] = Field(default_factory=list)
    before_verification: CommandEvidence
    execution_mode: Literal["STATIC_ONLY", "TRUSTED_PYTEST"]
    model_runtime: ModelRuntimeStatus
    safe_boundary: str


class AdhocFixResult(BaseModel):
    state: AdhocWorkspaceState
    proposal: WorkspaceFixProposal
    applied: bool
    rolled_back: bool
    after_verification: CommandEvidence
    final_status: Literal["VERIFIED_FIXED", "STATIC_CHECK_PASSED", "ROLLED_BACK"]
    patched_files: dict[str, str] = Field(default_factory=dict)
    audit: list[str] = Field(default_factory=list)

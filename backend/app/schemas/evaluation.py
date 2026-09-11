from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluationMetric(BaseModel):
    key: str
    label: str
    value: float = Field(ge=0.0, le=1.0)
    passed: int = Field(ge=0)
    total: int = Field(ge=0)
    description: str


class EvaluationCaseResult(BaseModel):
    case_id: str
    category: str
    title: str
    passed: bool
    expected: str
    observed: str
    details: dict[str, Any] = Field(default_factory=dict)


class EvaluationReport(BaseModel):
    generated_at: datetime
    benchmark_version: str
    deterministic: bool = True
    metrics: list[EvaluationMetric] = Field(default_factory=list)
    cases: list[EvaluationCaseResult] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)

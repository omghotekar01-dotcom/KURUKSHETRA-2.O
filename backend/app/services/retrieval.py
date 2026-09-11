from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from app.schemas.incident import IncidentRecord, KnowledgeMatch, ResolutionMemory


TOKEN_RE = re.compile(r"[a-z0-9_+-]+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "the", "to", "with", "after", "before",
    "this", "that", "users", "user", "service", "production",
}
DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "data" / "runbooks.json"


def _tokens(text: str) -> Counter[str]:
    return Counter(token for token in TOKEN_RE.findall(text.lower()) if token not in STOP_WORDS)


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left).intersection(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _score_candidate(query: Counter[str], component: str, record: IncidentRecord, text: str) -> float:
    lexical_score = _cosine(query, _tokens(text))
    component_bonus = 0.12 if component.lower() == record.triage.component.lower() else 0.0
    return min(1.0, lexical_score + component_bonus)


def retrieve_knowledge(
    record: IncidentRecord,
    memories: list[ResolutionMemory] | None = None,
    limit: int = 3,
    corpus_path: str | Path = DEFAULT_CORPUS,
) -> list[KnowledgeMatch]:
    """Retrieve runbooks plus verified resolution memory using a deterministic baseline."""
    entries = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
    query_text = " ".join(
        [
            record.incident.title,
            record.incident.description,
            *record.incident.logs,
            record.triage.component,
            *record.triage.signals,
        ]
    )
    query_tokens = _tokens(query_text)

    matches: list[KnowledgeMatch] = []
    for entry in entries:
        score = _score_candidate(
            query_tokens,
            entry["component"],
            record,
            f"{entry['issue']} {entry['fix']} {entry['component']}",
        )
        matches.append(
            KnowledgeMatch(
                id=entry["id"],
                component=entry["component"],
                issue=entry["issue"],
                fix=entry["fix"],
                source=entry["source"],
                score=round(score, 3),
            )
        )

    for memory in memories or []:
        if memory.incident_id == record.id:
            continue
        score = _score_candidate(
            query_tokens,
            memory.component,
            record,
            f"{memory.symptoms} {memory.working_hypothesis} {memory.remediation} {memory.component}",
        )
        matches.append(
            KnowledgeMatch(
                id=memory.memory_id,
                component=memory.component,
                issue=memory.symptoms,
                fix=memory.remediation,
                source=memory.source,
                score=round(score, 3),
            )
        )

    matches.sort(key=lambda item: item.score, reverse=True)
    return [match for match in matches[:limit] if match.score >= 0.18]


def retrieve_runbooks(
    record: IncidentRecord,
    limit: int = 3,
    corpus_path: str | Path = DEFAULT_CORPUS,
) -> list[KnowledgeMatch]:
    """Backward-compatible static-runbook retrieval used by baseline tests."""
    return retrieve_knowledge(record, memories=None, limit=limit, corpus_path=corpus_path)

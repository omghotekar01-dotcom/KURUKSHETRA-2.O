from __future__ import annotations

import os

from app.schemas.incident import IncidentIn, Severity, TriageResult


CATEGORY_RULES = [
    (("401", "403", "jwt", "oauth", "saml", "login", "authentication", "auth"), "Authentication", "auth-team"),
    (("postgres", "mysql", "database", "deadlock", "query", "sql", "connection pool"), "Database", "db-team"),
    (("502", "500", "api", "backend", "webhook", "worker", "uvicorn", "gunicorn"), "Backend", "backend-team"),
    (("react", "css", "button", "modal", "frontend", "ui", "browser"), "Frontend", "frontend-team"),
    (("kubernetes", "docker", "disk", "memory", "oom", "pod", "nginx", "infrastructure"), "Infrastructure", "platform-team"),
]

CRITICAL_SIGNALS = ("data loss", "security breach", "all users", "production down", "outage", "payment failure")
HIGH_SIGNALS = ("production", "500", "502", "401", "cannot login", "timeout", "failed", "unavailable")


def _configured_owner_map() -> dict[str, str]:
    """Read optional real-team routing without requiring a code change.

    Format:
        TRIAGE_OWNER_MAP=Authentication=identity-platform,Database=data-platform

    Invalid fragments are ignored and built-in safe defaults remain available.
    """
    raw = os.getenv("TRIAGE_OWNER_MAP", "").strip()
    owners: dict[str, str] = {}
    if not raw:
        return owners
    for fragment in raw.split(","):
        if "=" not in fragment:
            continue
        component, owner = fragment.split("=", 1)
        component = component.strip()
        owner = owner.strip()
        if component and owner:
            owners[component.casefold()] = owner[:120]
    return owners


def _owner_for(component: str, fallback: str) -> str:
    return _configured_owner_map().get(component.casefold(), fallback)


def _severity(text: str) -> Severity:
    if any(token in text for token in CRITICAL_SIGNALS):
        return Severity.critical
    if any(token in text for token in HIGH_SIGNALS):
        return Severity.high
    if any(token in text for token in ("degraded", "slow", "intermittent", "stale")):
        return Severity.medium
    return Severity.low


def triage_incident(incident: IncidentIn) -> TriageResult:
    text = f"{incident.title} {incident.description} {' '.join(incident.logs)}".lower()
    best_component = "Unclassified"
    best_team = _owner_for("Unclassified", "triage-team")
    best_hits: list[str] = []

    for keywords, component, default_team in CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in text]
        if len(hits) > len(best_hits):
            best_component = component
            best_team = _owner_for(component, default_team)
            best_hits = hits

    confidence = min(0.55 + (0.08 * len(best_hits)), 0.94) if best_hits else 0.35
    sev = _severity(text)
    summary = f"{best_component} incident in {incident.environment}: {incident.title.strip()}"

    return TriageResult(
        component=best_component,
        owner_team=best_team,
        severity=sev,
        confidence=round(confidence, 2),
        summary=summary,
        signals=best_hits[:6],
    )

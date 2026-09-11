from __future__ import annotations

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
    best_team = "triage-team"
    best_hits: list[str] = []

    for keywords, component, team in CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in text]
        if len(hits) > len(best_hits):
            best_component = component
            best_team = team
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

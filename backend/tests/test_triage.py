from app.schemas.incident import IncidentIn, Severity
from app.services.triage import triage_incident


def test_authentication_routing():
    result = triage_incident(
        IncidentIn(
            title="401 after login",
            description="Users receive 401 Unauthorized after a successful login in production.",
        )
    )
    assert result.component == "Authentication"
    assert result.owner_team == "auth-team"
    assert result.severity in {Severity.high, Severity.critical}
    assert result.confidence >= 0.55


def test_unknown_incident_stays_uncertain():
    result = triage_incident(
        IncidentIn(title="Unexpected behaviour", description="The workflow produces an unusual result.")
    )
    assert result.component == "Unclassified"
    assert result.confidence < 0.5

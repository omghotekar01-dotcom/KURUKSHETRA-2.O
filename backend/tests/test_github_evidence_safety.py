from datetime import datetime, timezone

from app.schemas.incident import IncidentIn, IncidentRecord, IncidentStatus
from app.services.github_context import _parse_patch_hunks
from app.services.triage import triage_incident


def test_repository_diff_hunks_redact_obvious_credentials() -> None:
    incident = IncidentIn(
        title="Authentication failure",
        description="JWT requests fail after deployment.",
        logs=["signature verification failed"],
    )
    now = datetime.now(timezone.utc)
    record = IncidentRecord(
        id="INC-SAFETY",
        created_at=now,
        updated_at=now,
        status=IncidentStatus.investigating,
        incident=incident,
        triage=triage_incident(incident),
        timeline=[],
    )
    patch = """@@ -1,2 +1,3 @@
 existing = True
+api_key=\"super-secret-value\"
+token_hint = \"jwt\"
"""

    hunks = _parse_patch_hunks(record, "auth/config.py", patch)

    assert len(hunks) == 1
    rendered = "\n".join(hunks[0].added_lines)
    assert "super-secret-value" not in rendered
    assert "[REDACTED]" in rendered

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.schemas.incident import (
    IncidentIn,
    IncidentRecord,
    IncidentStatus,
    IncidentSummary,
    ResolutionMemory,
    TimelineEvent,
    TriageResult,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentStore:
    """SQLite repository for incident state, audit history and verified memory."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @classmethod
    def from_env(cls) -> "IncidentStore":
        return cls(os.getenv("INCIDENT_DB_PATH", "data/incidents.db"))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    incident_json TEXT NOT NULL,
                    triage_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS timeline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS resolution_memory (
                    memory_id TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    component TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    symptoms TEXT NOT NULL,
                    working_hypothesis TEXT NOT NULL,
                    remediation TEXT NOT NULL,
                    verification_evidence TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'verified-resolution',
                    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_incidents_created_at
                ON incidents(created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_timeline_incident_id
                ON timeline_events(incident_id, id);

                CREATE INDEX IF NOT EXISTS idx_resolution_component
                ON resolution_memory(component, created_at DESC);
                """
            )

    def create(self, incident: IncidentIn, triage: TriageResult) -> IncidentRecord:
        incident_id = f"INC-{uuid4().hex[:10].upper()}"
        now = _utc_now()
        status = IncidentStatus.investigating

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO incidents(id, created_at, updated_at, status, incident_json, triage_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    now.isoformat(),
                    now.isoformat(),
                    status.value,
                    json.dumps(incident.model_dump(mode="json")),
                    json.dumps(triage.model_dump(mode="json")),
                ),
            )
            self._insert_event(
                connection,
                incident_id,
                now,
                "INTAKE",
                "Incident received and normalized.",
                {"environment": incident.environment},
            )
            self._insert_event(
                connection,
                incident_id,
                now,
                "TRIAGE",
                f"Routed to {triage.owner_team} as {triage.severity.value} severity.",
                {
                    "component": triage.component,
                    "confidence": triage.confidence,
                    "signals": triage.signals,
                },
            )

        record = self.get(incident_id)
        if record is None:  # pragma: no cover
            raise RuntimeError("Incident was written but could not be read back.")
        return record

    def get(self, incident_id: str) -> IncidentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if row is None:
                return None

            timeline_rows = connection.execute(
                """
                SELECT timestamp, stage, message, metadata_json
                FROM timeline_events
                WHERE incident_id = ?
                ORDER BY id ASC
                """,
                (incident_id,),
            ).fetchall()

        timeline = [
            TimelineEvent(
                timestamp=datetime.fromisoformat(event["timestamp"]),
                stage=event["stage"],
                message=event["message"],
                metadata=json.loads(event["metadata_json"]),
            )
            for event in timeline_rows
        ]

        return IncidentRecord(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=IncidentStatus(row["status"]),
            incident=IncidentIn.model_validate(json.loads(row["incident_json"])),
            triage=TriageResult.model_validate(json.loads(row["triage_json"])),
            timeline=timeline,
        )

    def list(self, limit: int = 50) -> list[IncidentSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()

        summaries: list[IncidentSummary] = []
        for row in rows:
            incident = IncidentIn.model_validate(json.loads(row["incident_json"]))
            triage = TriageResult.model_validate(json.loads(row["triage_json"]))
            summaries.append(
                IncidentSummary(
                    id=row["id"],
                    title=incident.title,
                    status=IncidentStatus(row["status"]),
                    severity=triage.severity,
                    component=triage.component,
                    owner_team=triage.owner_team,
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
            )
        return summaries

    def set_status(self, incident_id: str, status: IncidentStatus) -> IncidentRecord | None:
        now = _utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE incidents SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, now.isoformat(), incident_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(incident_id)

    def append_event(
        self,
        incident_id: str,
        stage: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> IncidentRecord | None:
        now = _utc_now()
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if exists is None:
                return None
            self._insert_event(connection, incident_id, now, stage, message, metadata or {})
            connection.execute(
                "UPDATE incidents SET updated_at = ? WHERE id = ?",
                (now.isoformat(), incident_id),
            )
        return self.get(incident_id)

    def save_resolution_memory(
        self,
        incident: IncidentRecord,
        working_hypothesis: str,
        remediation: str,
        verification_evidence: str,
    ) -> ResolutionMemory:
        now = _utc_now()
        existing = self.get_resolution_memory(incident.id)
        memory_id = existing.memory_id if existing else f"MEM-{uuid4().hex[:10].upper()}"
        symptoms = f"{incident.incident.title}. {incident.incident.description}".strip()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO resolution_memory(
                    memory_id, incident_id, created_at, component, severity, symptoms,
                    working_hypothesis, remediation, verification_evidence, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(incident_id) DO UPDATE SET
                    created_at = excluded.created_at,
                    component = excluded.component,
                    severity = excluded.severity,
                    symptoms = excluded.symptoms,
                    working_hypothesis = excluded.working_hypothesis,
                    remediation = excluded.remediation,
                    verification_evidence = excluded.verification_evidence,
                    source = excluded.source
                """,
                (
                    memory_id,
                    incident.id,
                    now.isoformat(),
                    incident.triage.component,
                    incident.triage.severity.value,
                    symptoms,
                    working_hypothesis,
                    remediation,
                    verification_evidence,
                    "verified-resolution",
                ),
            )

        memory = self.get_resolution_memory(incident.id)
        if memory is None:  # pragma: no cover
            raise RuntimeError("Resolution memory was written but could not be read back.")
        return memory

    def get_resolution_memory(self, incident_id: str) -> ResolutionMemory | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM resolution_memory WHERE incident_id = ?", (incident_id,)
            ).fetchone()
        return self._memory_from_row(row) if row else None

    def list_resolution_memory(self, limit: int = 50) -> list[ResolutionMemory]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM resolution_memory ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._memory_from_row(row) for row in rows]

    def _memory_from_row(self, row: sqlite3.Row) -> ResolutionMemory:
        return ResolutionMemory(
            memory_id=row["memory_id"],
            incident_id=row["incident_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            component=row["component"],
            severity=row["severity"],
            symptoms=row["symptoms"],
            working_hypothesis=row["working_hypothesis"],
            remediation=row["remediation"],
            verification_evidence=row["verification_evidence"],
            source=row["source"],
        )

    def _insert_event(
        self,
        connection: sqlite3.Connection,
        incident_id: str,
        timestamp: datetime,
        stage: str,
        message: str,
        metadata: dict[str, Any],
    ) -> None:
        connection.execute(
            """
            INSERT INTO timeline_events(incident_id, timestamp, stage, message, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                timestamp.isoformat(),
                stage,
                message,
                json.dumps(metadata),
            ),
        )

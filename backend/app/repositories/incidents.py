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
    TimelineEvent,
    TriageResult,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentStore:
    """Small SQLite repository used by the hackathon build and demo mode."""

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

                CREATE INDEX IF NOT EXISTS idx_incidents_created_at
                ON incidents(created_at DESC);

                CREATE INDEX IF NOT EXISTS idx_timeline_incident_id
                ON timeline_events(incident_id, id);
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
        if record is None:  # pragma: no cover - defensive consistency check
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

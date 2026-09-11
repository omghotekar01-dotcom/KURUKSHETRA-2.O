# DATA, API AND STATE CONTRACTS

Last updated: 2026-09-11
Status: **WAITING_FOR_PS — PROVISIONAL SHAPES ONLY**

This file prevents frontend/backend/agent modules from inventing incompatible field names. Nothing here is final until the exact PS and architecture are frozen.

## Core incident object — provisional

```json
{
  "id": "INC-001",
  "title": "401 after login",
  "raw_report": "Users get 401 after entering valid credentials",
  "summary": "Authentication fails after successful credential entry",
  "category": "authentication",
  "component": "auth-service",
  "severity": "high",
  "status": "investigating",
  "owner": "auth-team",
  "confidence": 0.91,
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Evidence object

```json
{
  "id": "EV-001",
  "incident_id": "INC-001",
  "type": "runbook|historical_incident|github_commit|log|user_input",
  "source": "string",
  "title": "string",
  "content": "string",
  "relevance": 0.84,
  "timestamp": "ISO-8601|null",
  "metadata": {}
}
```

## Root-cause hypothesis object

```json
{
  "id": "RCA-1",
  "hypothesis": "JWT signing secret mismatch after deployment",
  "confidence": 0.82,
  "evidence_for": ["EV-001", "EV-002"],
  "evidence_against": [],
  "missing_information": []
}
```

## Remediation object

```json
{
  "id": "REM-1",
  "incident_id": "INC-001",
  "action_type": "create_github_issue",
  "description": "Create an issue for auth configuration verification",
  "risk": "low",
  "requires_approval": false,
  "verification_plan": "Confirm issue creation and attach RCA evidence",
  "parameters": {}
}
```

## Approval object

```json
{
  "id": "APR-1",
  "action_id": "REM-1",
  "decision": "approve|edit|reject",
  "approved_by": "user-or-demo-identity",
  "approved_at": "ISO-8601",
  "bound_parameters_hash": "optional"
}
```

## Action result

```json
{
  "action_id": "REM-1",
  "status": "success|failed|cancelled",
  "external_id": "optional",
  "external_url": "optional",
  "message": "string",
  "executed_at": "ISO-8601"
}
```

## Verification object

```json
{
  "incident_id": "INC-001",
  "status": "pass|fail|inconclusive",
  "method": "test|manual|api_check|demo_rule",
  "evidence": [],
  "verified_at": "ISO-8601"
}
```

## Suggested REST API surface — provisional

```text
POST   /api/v1/incidents
GET    /api/v1/incidents
GET    /api/v1/incidents/{id}
POST   /api/v1/incidents/{id}/investigate
GET    /api/v1/incidents/{id}/evidence
GET    /api/v1/incidents/{id}/hypotheses
POST   /api/v1/incidents/{id}/remediations
POST   /api/v1/actions/{id}/approve
POST   /api/v1/actions/{id}/reject
POST   /api/v1/actions/{id}/execute
POST   /api/v1/incidents/{id}/verify
GET    /api/v1/metrics
```

Do not implement all endpoints merely because they are listed. Freeze only what the final UI/golden path needs.

## Standard success envelope — option

```json
{
  "success": true,
  "data": {},
  "message": "optional"
}
```

## Standard error envelope

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Human-readable description",
    "details": {}
  }
}
```

## Agent state — provisional

```text
incident
triage
collected_evidence[]
retrieved_memory[]
hypotheses[]
selected_remediation
risk_decision
approval
execution_result
verification
messages/logs
```

## Database entities — provisional

- `incidents`
- `evidence`
- `hypotheses`
- `remediations`
- `approvals`
- `actions`
- `verification_results`
- `historical_incidents`
- `agent_runs`
- `integrations`

## Contract rules

1. Frontend may mock responses, but mocks must exactly match frozen schemas.
2. Do not silently rename keys.
3. Any contract change after freeze is a **BREAKING CHANGE**.
4. LLM outputs must be validated before entering shared state.
5. IDs/status enums must be centrally defined.
6. Never return secrets/tokens in API payloads.
7. Preserve provenance for evidence.

## Waiting for PS

Before implementation, finalize:
- exact fields;
- endpoint list;
- DB engine;
- enum values;
- pagination/filtering;
- authentication requirement;
- streaming/SSE/WebSocket requirement;
- persistence strategy;
- actual external action schema.
# ARCHITECTURE PLAYBOOK

## Target architecture

```text
Incident Intake
   ↓
FastAPI API Layer
   ↓
Incident State / PostgreSQL
   ↓
LangGraph Supervisor
   ├─ Triage Agent
   ├─ Evidence Collector
   ├─ Historical RAG Retriever
   ├─ RCA / Hypothesis Agent
   ├─ Remediation Planner
   ├─ Risk / Policy Gate
   └─ Verification Agent
   ↓
Human Approval
   ↓
Bounded Action Layer
   ├─ GitHub issue / draft PR
   ├─ Gmail / Slack notification
   └─ local/demo remediation action
   ↓
Verification
   ↓
Incident Memory + Analytics
```

## Frontend

Recommended:
- React;
- Vite;
- TypeScript;
- Tailwind CSS;
- shadcn/ui;
- TanStack Query;
- Recharts;
- React Router.

Core screens:

1. **New Incident** — bug/incident input, optional logs/repo/environment.
2. **Live Investigation** — streaming/current steps, evidence and hypotheses.
3. **Incident Details** — severity, owner, RCA, remediation, action gate, timeline.
4. **Incidents** — searchable list and status.
5. **Knowledge Base** — runbooks and historical incidents.
6. **Evaluation Lab** — benchmark scenarios and scores.
7. **Settings/Integrations** — GitHub/Gmail/Slack/demo configuration.

## Backend

Recommended:
- Python 3.11+;
- FastAPI;
- Uvicorn;
- Pydantic;
- SQLAlchemy;
- PostgreSQL;
- SQLite fallback.

Suggested modules:

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    agents/
    rag/
    integrations/
    policies/
    evaluation/
    tests/
```

## Agent state

Prefer strongly typed state over free-form dictionaries.

Suggested state fields:

- incident_id;
- raw_report;
- environment;
- repo;
- suspected_component;
- severity;
- owner_team;
- evidence[];
- historical_matches[];
- hypotheses[];
- proposed_actions[];
- selected_action;
- risk_level;
- approval_status;
- verification_plan;
- verification_result;
- final_status;
- timeline[].

## Evidence object

Every important claim should map to evidence.

Suggested schema:

```json
{
  "id": "ev_001",
  "type": "git_commit|runbook|historical_incident|log|user_report|test_result",
  "source": "...",
  "timestamp": "...",
  "summary": "...",
  "relevance": 0.86,
  "trust": 0.92,
  "metadata": {}
}
```

## Hypothesis object

```json
{
  "id": "hyp_001",
  "title": "JWT secret mismatch after deployment",
  "confidence": 0.84,
  "evidence_for": ["ev_001", "ev_004"],
  "evidence_against": ["ev_007"],
  "next_diagnostic": "Compare runtime JWT secret version to deployment configuration"
}
```

This is preferable to a single opaque “root cause” paragraph.

## RAG

Hackathon default:
- Sentence Transformers embeddings;
- FAISS;
- local runbooks;
- historical incident records;
- optionally GitHub issues.

Retrieval flow:

```text
incident summary
→ embedding
→ top-k retrieval
→ metadata/category filtering
→ relevance threshold
→ evidence objects
→ RCA agent
```

Do not feed every retrieved item to the LLM. Use top-k plus thresholds.

## Risk / policy gate

Actions should be classified by consequence.

### LOW
Examples:
- create internal note;
- create GitHub issue;
- draft email;
- notify Slack;
- generate patch without applying.

Can be auto-prepared. Execution can be allowed in demo depending on configuration.

### MEDIUM
Examples:
- create code branch;
- apply patch;
- open draft PR;
- trigger non-production tests.

Require explicit human approval.

### HIGH
Examples:
- deploy;
- restart production service;
- mutate production database;
- change IAM/security policy;
- delete data;
- merge to protected branch.

Never auto-execute in the hackathon prototype. Show the proposed action and explain that production-grade deployment requires external policy/approval systems.

## Verification

Every remediation needs a verification plan.

Possible verification methods:
- unit test;
- integration test;
- reproduction script;
- static check;
- expected HTTP response;
- simulated health metric;
- user confirmation.

The UI should distinguish:
- proposed;
- approved;
- executed;
- verification pending;
- verified;
- failed;
- escalated.

## GitHub integration

Prefer bounded capabilities:

P0:
- read repo metadata;
- read issues/recent commits;
- create issue.

P1:
- create branch;
- commit a small generated patch;
- open draft PR;
- attach RCA and verification plan.

Safety:
- never push to `main`;
- never auto-merge;
- never bypass branch protection;
- use dedicated agent branch;
- keep human review before merge.

## Failure modes and fallbacks

### LLM unavailable
- deterministic rule-based category fallback;
- use cached demo responses for known demo incidents.

### Embedding/RAG unavailable
- keyword/BM25-like fallback or direct local search.

### GitHub unavailable
- show prepared action payload and save to action log instead of execution.

### Database unavailable
- SQLite or in-memory demo mode.

### Gmail/Slack unavailable
- local notification preview.

The demo should remain useful even when external network calls fail.

## Observability of our own agent

Log:
- node start/end;
- tool calls;
- evidence retrieved;
- latency;
- token/model usage where available;
- confidence;
- policy verdict;
- approval;
- action result;
- verification result;
- errors.

Do not expose secrets or full sensitive logs.

## Evaluation architecture

Store benchmark scenarios in version-controlled JSON/YAML.

Each scenario should include:
- incident text;
- optional logs;
- expected category;
- expected severity range;
- relevant runbook/incident IDs;
- expected root cause or accepted alternatives;
- unsafe actions that must not occur;
- expected verification.

Evaluation should be runnable from CLI/backend and surfaced in UI.

## Architecture freeze rule

Once shared schemas and API contracts are accepted, no AI assistant should regenerate the project into a new structure. Make targeted changes and explicitly mark breaking migrations.
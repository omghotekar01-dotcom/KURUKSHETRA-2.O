# ARCHITECTURE RESEARCH

Last updated: 2026-09-11

Purpose: capture current architecture lessons from modern AI-SRE/debugging/coding-agent systems and translate them into build decisions for Kurukshetra. This file complements `ARCHITECTURE_PLAYBOOK.md`: the playbook is our provisional design; this file records why certain architecture choices are attractive or dangerous.

## 1. Market architecture pattern: context aggregation before action

Modern AI debugging/SRE products increasingly gather context from multiple sources instead of relying on a single bug report. Relevant sources include:
- runtime errors;
- logs;
- traces;
- metrics;
- recent deploys;
- Git history;
- repository code;
- runbooks;
- historical incidents;
- team conversations.

Architecture implication:
Our product should normalize evidence into a common representation before asking the RCA agent to reason over it.

Avoid:
```text
raw incident + giant prompt containing everything
```

Prefer:
```text
collect → normalize → rank → select → reason
```

This gives better explainability and reduces noisy-context failure.

## 2. Runtime context matters

Source-code-only agents can reason about code structure, but many real incidents are only understandable through runtime signals. Sentry's Seer positioning explicitly emphasizes combining runtime context (errors/traces/logs/etc.) with code/history.

Hackathon implication:
We do not need to build a production telemetry platform, but we should design the input model to accept evidence types such as logs, HTTP errors, synthetic metrics or recent deployment metadata.

A convincing demo can use deterministic fixtures:
- `sample_logs.json`;
- recent commits from the project/test repo;
- runbook entries;
- expected health signal.

This lets us demonstrate runtime-aware reasoning without recreating Datadog.

## 3. Persistent agent state is valuable

Long-running investigations need state across steps, human review and failures. LangGraph persistence/checkpointing supports exactly this style of workflow.

Recommended incident thread model:

```text
thread_id == incident_id
```

Persist after major stages:
- intake;
- triage;
- evidence collection;
- RCA;
- proposed action;
- human decision;
- execution;
- verification.

Benefit:
- resume after API/tool failure;
- show timeline/history;
- support human approval without restarting investigation;
- debug agent behavior.

Hackathon fallback:
If persistent LangGraph checkpointing is too time-consuming, persist our own incident stage/state in PostgreSQL/SQLite and keep LangGraph orchestration simple.

## 4. Human approval should be a workflow primitive

Do not bolt an “Approve” button onto the UI after the agent has already executed the action.

Correct architecture:

```text
proposal generated
→ policy engine evaluates
→ graph interrupts / status=PENDING_APPROVAL
→ UI displays exact action
→ user approves/edits/rejects
→ workflow resumes
```

This makes approval real rather than cosmetic.

## 5. Coding-agent handoff vs building our own coding agent

GitHub's current agent workflows and products like Sentry Seer already hand rich issue context to coding agents that create branches/PRs.

Therefore we should not spend the entire hackathon building a full autonomous coding environment from scratch unless the PS demands it.

Better product architecture:

```text
Incident Intelligence Layer
  ↓
Structured remediation package
  ↓
GitHub Issue / Draft PR / Coding-agent handoff
```

Remediation package fields:
- incident summary;
- suspected root cause;
- evidence references;
- affected files/modules;
- suggested changes;
- constraints;
- verification/tests;
- risk classification.

This itself is useful and interoperable.

## 6. Evidence graph vs simple relational storage

An actual graph database may look impressive but can consume valuable hackathon time.

Logical evidence graph:
```text
Incident
 ├─ evidence → Commit A
 ├─ evidence → Log line B
 ├─ similar_to → Incident 17
 ├─ hypothesis → H1
 └─ hypothesis → H2

H1
 ├─ supported_by → Commit A
 ├─ supported_by → Log B
 └─ contradicted_by → Metric C
```

Implementation options:

### Option A — PostgreSQL/JSON
Fastest. Store relationships through IDs/arrays/association tables.

### Option B — NetworkX in memory
Useful for visualization/reasoning experiments without new infrastructure.

### Option C — Neo4j
Only if graph traversal is core to the PS and team already knows it.

Default recommendation for 24 hours: Option A, with graph-like data model and graph visualization on frontend if useful.

## 7. Multi-agent architecture should earn its complexity

Do not create 15 agents for presentation value.

A practical decomposition:

1. **Triage** — category/severity/owner.
2. **Evidence Collector** — tools/retrieval, not necessarily LLM-heavy.
3. **RCA** — ranked hypotheses.
4. **Remediation Planner** — actions + verification.
5. **Policy Gate** — preferably deterministic rules plus optional LLM explanation.
6. **Verification** — test/result interpretation.

Some “agents” can simply be deterministic services. This reduces cost and failure modes.

## 8. Structured outputs over brittle parsing

Never parse critical LLM output with assumptions like:

```python
lines[0]
lines[1]
lines[2]
```

Use Pydantic/JSON structured outputs for:
- triage result;
- evidence relevance;
- hypothesis list;
- remediation plan;
- risk explanation.

Example:

```json
{
  "component": "authentication",
  "severity": "high",
  "owner": "auth-team",
  "summary": "JWT validation fails after deployment",
  "confidence": 0.82
}
```

Validate server-side before storing or executing anything.

## 9. Confidence should combine signals

Raw LLM self-confidence is weak.

Possible composite confidence:

```text
RCA confidence =
  retrieval support
+ independent evidence support
+ historical similarity
- contradiction penalty
- missing-data penalty
```

For prototype, use interpretable weighted heuristics rather than pretending to have a calibrated probabilistic model.

Always label it as a system confidence score, not scientific probability, unless calibrated against benchmarks.

## 10. Retrieval architecture

Start simple:
- local runbooks;
- historical incidents;
- GitHub issues optionally.

Pipeline:

```text
raw incident
→ concise structured incident representation
→ embedding query
→ metadata filters
→ vector retrieval top-k
→ rerank / threshold
→ evidence objects
```

Potential metadata:
- component;
- environment;
- error code;
- severity;
- technology;
- resolved/unresolved;
- remediation success.

Do not retrieve only by category because cross-component incidents are common.

## 11. Tool architecture

Wrap every external action behind an adapter with explicit schema.

Example interfaces:

```text
GitHubAdapter
- get_recent_commits()
- get_issue()
- create_issue()
- create_draft_pr()

NotificationAdapter
- draft_message()
- send_message()

VerificationAdapter
- run_test_suite()
- run_health_check()
```

Never expose one unrestricted “execute whatever command the LLM writes” tool in the MVP.

## 12. Integration architecture

Recommended stack boundary:

```text
React Frontend
  ↕ REST/SSE/WebSocket(optional)
FastAPI
  ↕
Incident Service / DB
  ↕
LangGraph workflow
  ├─ RAG service
  ├─ GitHub adapter
  ├─ LLM adapter
  ├─ policy service
  └─ verification service
```

For 24 hours, prefer REST + polling or Server-Sent Events over a complex event bus.

Do not add Kafka/Redis unless a real requirement appears.

## 13. Streaming investigation UX

Even if backend work is sequential, the UI can show state transitions:

```text
Analyzing incident ✓
Collecting evidence ✓
Searching similar incidents ✓
Ranking hypotheses …
Planning remediation
Waiting for approval
```

This makes agent work understandable and reduces perceived latency.

Implementation options:
- polling `GET /incidents/{id}` every 1–2 seconds;
- SSE for stage events;
- WebSocket only if already comfortable.

Default: polling first; upgrade to SSE only if needed.

## 14. Database architecture

Likely entities:

```text
Incident
IncidentEvent
Evidence
Hypothesis
HistoricalMatch
RemediationPlan
Approval
ActionExecution
Verification
IntegrationConfig
EvaluationRun
EvaluationCaseResult
```

Keep raw external payloads in JSON fields when schema may evolve quickly, while extracting important searchable fields into columns.

## 15. Incident memory

The useful memory unit is not a chat transcript.

A resolved memory should contain:
- symptoms;
- environment;
- relevant evidence;
- root cause;
- successful/failed actions;
- verification result;
- time to resolution;
- recurrence tags;
- source incident ID.

RAG should prefer verified/resolved incidents over unverified recommendations.

## 16. Demo resilience architecture

Support explicit modes:

```text
APP_MODE=demo
APP_MODE=live
```

Demo mode:
- fixture incidents;
- local embeddings/index;
- SQLite or local Postgres;
- mocked notification fallback;
- controlled GitHub repo or no-write simulation;
- cached/predefined LLM fallback for golden scenario if provider is unavailable.

Live mode:
- real LLM;
- real GitHub API;
- configured notifications;
- persistent DB.

The UI should display when fallback/demo mode is active so the team does not accidentally misrepresent mocked actions as live production behavior.

## 17. Architecture decisions we should avoid prematurely

Do not freeze yet:
- exact LLM provider;
- exact vector store;
- exact cloud deployment;
- graph database;
- Slack vs Gmail vs Teams;
- coding-agent integration.

Freeze only after exact PS, available credentials/network and team familiarity are known.

## 18. Architecture success criteria

Our architecture is good enough when:
- one incident can complete the golden path end to end;
- components can be developed independently with stable contracts;
- external failures degrade gracefully;
- risk actions pause correctly;
- evidence is visible to the user;
- verification can contradict the proposed fix;
- state survives/reloads;
- the repository remains easy to clone and run.

Anything beyond that should justify its implementation time.

## Current research conclusion

The strongest architecture for this hackathon is not “maximum number of agents.” It is a small, inspectable, evidence-first state machine that can gather context, express uncertainty, ask for approval at the right boundary, perform one or two bounded actions, verify them, and preserve structured incident memory.

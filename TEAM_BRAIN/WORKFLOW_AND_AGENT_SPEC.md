# WORKFLOW AND AGENT SPECIFICATION

Last updated: 2026-09-11
Status: **PROVISIONAL — FINALIZE AFTER PS**

## Objective

Define the intended closed-loop workflow and clear agent/module boundaries so implementation does not collapse into one giant prompt.

## Canonical workflow

```text
INCIDENT INTAKE
   ↓
NORMALIZE / STRUCTURE
   ↓
TRIAGE: category + severity + owner + confidence
   ↓
EVIDENCE COLLECTION
   ├─ runbooks
   ├─ historical incidents
   ├─ GitHub context
   └─ supplied logs/errors
   ↓
RAG / SIMILARITY SEARCH
   ↓
ROOT-CAUSE HYPOTHESES
   ↓
REMEDIATION OPTIONS
   ↓
RISK + POLICY GATE
   ↓
HUMAN APPROVAL IF REQUIRED
   ↓
BOUNDED ACTION
   ↓
VERIFICATION
   ↓
INCIDENT TIMELINE + MEMORY
```

## Suggested logical agents/modules

These are logical responsibilities, not necessarily separate LLM calls. For a 24-hour build, combine modules when it reduces latency and complexity without harming clarity.

### 1. Intake Normalizer
Input:
- raw incident text;
- optional logs/metadata.

Output:
- normalized incident object;
- extracted environment/service/error hints;
- preserved raw input.

### 2. Triage Agent
Input:
- normalized incident.

Output:
- category/component;
- severity;
- likely owner;
- concise summary;
- confidence.

Must support UNKNOWN/UNCLASSIFIED.

### 3. Evidence Collector
Input:
- incident + permitted integrations.

Output:
- typed evidence objects with source, timestamp, relevance and content/snippet.

Do not convert unsupported guesses into evidence.

### 4. Retrieval Agent
Input:
- incident summary + evidence/query terms.

Output:
- top-k historical incidents/runbook entries;
- similarity/relevance scores;
- provenance.

### 5. RCA Agent
Input:
- incident + retrieved evidence.

Output:
- ranked hypotheses;
- evidence-for/evidence-against;
- confidence;
- missing information request when needed.

### 6. Remediation Agent
Input:
- top hypotheses + constraints.

Output:
- candidate remediation;
- expected effect;
- prerequisites;
- rollback/fallback;
- verification plan.

### 7. Risk/Policy Engine
Prefer deterministic rules plus structured model output rather than LLM-only authorization.

Input:
- proposed action;
- target system;
- confidence;
- action type.

Output:
- LOW / MEDIUM / HIGH risk;
- allowed / approval_required / forbidden;
- reason.

### 8. Approval Gate
Input:
- exact action parameters + evidence + risk.

Output:
- approve / edit / reject;
- approver metadata.

### 9. Execution Adapter
Prototype examples:
- create GitHub issue;
- create branch/draft PR if safely scoped;
- send Gmail/Slack notification.

Output:
- action ID/URL/status/error.

### 10. Verification Agent
Input:
- action result + defined verification plan.

Output:
- PASS / FAIL / INCONCLUSIVE;
- evidence;
- next step.

### 11. Memory Writer
Stores only structured, useful resolution knowledge:
- symptoms;
- environment;
- root cause;
- successful/failed actions;
- verification;
- tags/components.

## State machine — provisional

```text
NEW
→ TRIAGING
→ INVESTIGATING
→ RCA_READY
→ REMEDIATION_READY
→ AWAITING_APPROVAL (if needed)
→ EXECUTING
→ VERIFYING
→ RESOLVED
```

Alternative exits:

```text
ESCALATED
FAILED_ACTION
INSUFFICIENT_EVIDENCE
REJECTED
```

## Orchestration guidance

LangGraph is a strong fit because the workflow has explicit state, tool calls, branching and human interrupts. Do not use LangGraph merely to draw a linear graph if plain Python would be simpler. Use it where durable state/conditional routing/approval makes the workflow clearer.

## Structured output rule

LLM components should use JSON/Pydantic-like schemas. Avoid fragile parsing such as assuming line 1 is category, line 2 is email, line 3 is summary.

## Human steering

The UI should allow a user to:
- add context;
- correct category/owner;
- reject a hypothesis;
- edit a proposed action;
- request deeper investigation.

Corrections should be logged and can later become evaluation/learning data.

## Finalization after PS

Freeze:
- actual agent count;
- exact state schema;
- exact branching logic;
- tool permissions;
- input/output Pydantic models;
- latency budget;
- which modules use LLM vs deterministic rules;
- which actions are actually implemented in the hackathon.
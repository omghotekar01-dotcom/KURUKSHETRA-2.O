# CANONICAL PROJECT DESCRIPTION

Last updated: 2026-09-11
Status: **PROVISIONAL — FINAL PROJECT NOT FROZEN UNTIL EXACT PS IS LOCKED**

Use this file whenever a teammate, AI assistant, mentor or judge-prep session asks: “What exactly are we building?”

## Current working direction

We are investigating a startup-level **agentic engineering incident-response platform** that helps software teams move from a raw bug/incident report to an evidence-backed, risk-aware, verifiable action faster than a human manually reconstructing context across code, runbooks, previous incidents and team tools.

The concept started from a simple reference pattern — classify a bug, retrieve a known fix with RAG, draft a response and dispatch it — but our target is a substantially more complete closed-loop system.

## One-line working pitch

**An AI incident commander that investigates across code, history and runbooks, ranks likely root causes, proposes remediation, gates risky actions through human approval, verifies outcomes, and remembers what worked.**

## Simple explanation

A user reports something like:

> “Users started getting 401 errors after today’s deployment.”

Instead of a developer manually reading the report, finding the right team, checking recent commits, searching old tickets/runbooks, guessing a root cause, writing an escalation and later checking whether the fix worked, the system should progressively do those steps in one auditable workflow.

## Target end-to-end lifecycle

```text
Incident / bug / CI failure / pasted logs
        ↓
Understand + classify + severity + ownership
        ↓
Collect evidence from allowed sources
        ↓
Retrieve similar incidents / runbooks
        ↓
Generate and rank root-cause hypotheses
        ↓
Generate remediation options + verification plan
        ↓
Risk/confidence gate
        ↓
Human approval for consequential action
        ↓
Execute bounded action (e.g. issue, draft PR, notification)
        ↓
Verify result
        ↓
Update timeline + structured incident memory
```

## What makes this more than a chatbot

A normal LLM conversation can summarize a pasted error. The proposed product should instead combine:

- structured incident state;
- explicit evidence objects;
- historical memory/RAG;
- repository or workflow context;
- multiple ranked hypotheses;
- confidence/risk representation;
- tools/integrations;
- human approval;
- bounded action execution;
- verification;
- audit trail;
- repeatable evaluation.

## Core product promise

**From incident to evidence-backed action in minutes — with humans controlling risky steps.**

## Current likely prototype user

Engineering teams, especially smaller SaaS/startup teams that use GitHub plus lightweight monitoring/runbooks and do not have a large SRE organization.

This user selection is provisional until the actual PS is frozen.

## Primary user pains we are targeting

During an incident, teams repeatedly ask:

1. What broke?
2. How severe is it?
3. Who owns it?
4. What changed recently?
5. Have we seen this before?
6. What evidence supports the likely root cause?
7. What should we do next?
8. Is the action safe?
9. Did it work?
10. What should we remember for next time?

## Proposed differentiators under investigation

1. **Evidence-backed RCA** — recommendations visibly tied to evidence, not hidden reasoning.
2. **Multiple hypotheses** — system can represent uncertainty instead of pretending the first answer is certain.
3. **Risk-aware action gate** — autonomy is based on consequence as well as model confidence.
4. **Verification-first remediation** — a proposed fix is not called successful until a check passes.
5. **Structured incident memory** — preserve root cause, action, environment and verified outcome for future retrieval.
6. **Evaluation Lab** — show repeatable benchmark/regression behavior instead of one scripted demo.
7. **Lightweight startup-friendly deployment** — useful without requiring an expensive full observability platform.

## P0 working concept

The minimum strong prototype should aim to demonstrate one complete golden path:

1. submit/import incident;
2. classify category/component/severity;
3. show evidence collection;
4. retrieve similar historical incident/runbook;
5. show ranked root-cause hypothesis with confidence;
6. recommend remediation and verification plan;
7. show action risk;
8. require human approval for medium-risk action;
9. perform one real bounded integration such as GitHub issue/draft PR or team notification;
10. show verification result;
11. update incident status/history.

## What this project is NOT

Unless the exact PS demands otherwise, this is not:

- a generic chatbot;
- a clone of Sentry/Datadog/PagerDuty;
- a full observability ingestion platform;
- an autonomous production deployer;
- an LLM that can silently merge to `main`;
- a simple “bug classifier + email sender”;
- a giant model-training project;
- a promise that AI can always identify root cause correctly.

## Reference inspiration

The public repository `whitespace-24/Agentic-Bug-Router-and-Dispatcher` is treated only as a simple reference architecture for LangGraph + LLM classification + local RAG + Gmail MCP. We must not submit a near-copy.

## Finalization trigger

When the exact Kurukshetra problem statement is selected, replace the provisional portions of this file with:

- exact PS text/ID;
- exact target user;
- exact project name/tagline;
- exact problem framing;
- exact architecture scope;
- exact P0/P1/P2 list;
- exact measurable success criteria;
- exact judge-facing differentiation.

Until then, this file describes the current research direction, not a frozen submission.
# KURUKSHETRA 2.0 — TEAM BRAIN

This directory is the shared research, strategy, prompt, architecture, experiment, safety, evaluation and decision memory for the Kurukshetra 2.0 project.

> Branch policy: this material lives on `develop` during active work. The repository is public, so nothing committed here should be treated as secret or hidden from reviewers.

## Why this exists

We are building under a 24-hour hackathon constraint, but we want the quality bar of a real startup/research prototype. The purpose of TEAM_BRAIN is to prevent repeated thinking, lost decisions, contradictory AI outputs, random stack changes, duplicate work and context loss across ChatGPT, Codex, Astra and teammate sessions.

## Operating principles

1. Research before architecture changes.
2. Preserve the shared repository structure and contracts.
3. Prefer a reliable closed-loop MVP over a giant half-working system.
4. Distinguish evidence from assumptions.
5. Record major decisions and reversals.
6. Keep risky autonomous actions behind explicit human approval.
7. Evaluate agents with repeatable scenarios instead of demo-only anecdotes.
8. Design for graceful degradation if LLM/API/integration services fail.
9. Maintain a deterministic demo path.
10. Update `docs/PROJECT_STATUS.md` after meaningful milestones.
11. Do not inflate this knowledge base with repetitive filler; each addition should add evidence, a decision, a reusable prompt, an experiment, or an implementation insight.
12. Use `A_TO_Z_INDEX.md` as the canonical completeness map and resolve gaps rather than duplicating documents.

## Mandatory reading order for any new AI/team session

1. `TEAM_BRAIN/README.md`
2. `TEAM_BRAIN/A_TO_Z_INDEX.md`
3. `docs/PROJECT_STATUS.md`
4. `TEAM_BRAIN/EVENT_AND_CONSTRAINTS.md`
5. `TEAM_BRAIN/CANONICAL_PROJECT_DESCRIPTION.md`
6. `TEAM_BRAIN/DECISION_LOG.md`
7. Relevant technical/product/safety/evaluation files
8. Existing code/contracts before proposing changes

## Directory map

### Orientation / continuity
- `A_TO_Z_INDEX.md` — canonical completeness matrix from architecture to zero-to-demo.
- `EVENT_AND_CONSTRAINTS.md` — event facts, timeline and known/unknown constraints.
- `CANONICAL_PROJECT_DESCRIPTION.md` — single source for what the current project direction actually is.
- `PROJECT_DESCRIPTION_TEMPLATES.md` — 10s/30s/60s/technical/business descriptions for consistent communication.
- `GLOSSARY_AND_ACRONYMS.md` — shared vocabulary and terms we must not misuse.
- `CLAIMS_AND_EVIDENCE_LEDGER.md` — prevents unsupported metrics, novelty and capability claims.
- `MASTER_PROMPT.md` — permanent project-wide AI operating prompt.
- `DECISION_LOG.md` — durable architecture/product decisions and their reasons.

### Research / strategy / market
- `RESEARCH_LEDGER.md` — rolling research findings and market/problem observations.
- `SOURCES.md` — evidence sources and links.
- `PRODUCT_STRATEGY.md` — product thesis, users, workflow, moat and MVP/P1/P2 priorities.
- `PROBLEM_USERS_AND_PERSONAS.md` — pain model, provisional users/personas and jobs-to-be-done.
- `COMPETITOR_GAPS.md` — current incident-response / AI debugging capabilities and where we should differentiate.
- `BUSINESS_STARTUP_AND_GTM.md` — startup wedge, buyer, value, moat and GTM hypotheses.

### Requirements / architecture / workflow
- `REQUIREMENTS_CATALOG.md` — functional/safety/hackathon requirements and acceptance criteria.
- `ARCHITECTURE_PLAYBOOK.md` — provisional target architecture, system boundaries and integration rules.
- `ARCHITECTURE_RESEARCH.md` — architectural evidence, tradeoffs and lessons from current products/research.
- `WORKFLOW_AND_AGENT_SPEC.md` — canonical incident lifecycle and logical agent/module responsibilities.
- `DATA_API_AND_STATE_CONTRACTS.md` — provisional shared schemas, API surface and agent state.
- `RAG_AND_KNOWLEDGE_DESIGN.md` — runbooks, incident memory, retrieval and evaluation design.
- `TECH_STACK_AND_DEPENDENCIES.md` — provisional practical stack and dependency-risk rules.
- `UX_UI_SPEC.md` — judge/user-facing screens, flow, explainability and frontend rules.
- `NONFUNCTIONAL_REQUIREMENTS.md` — reliability, latency, security, auditability, portability and usability requirements.

### Security / evaluation / quality
- `SECURITY_AND_GUARDRAILS.md` — autonomy boundaries, approval policy, Git/tool safety, prompt-injection handling and audit rules.
- `EVALUATION_FRAMEWORK.md` — benchmark design, metrics, regression gates and demo acceptance tests.
- `INCIDENT_TAXONOMY_AND_TEST_SCENARIOS.md` — repeatable incident classes and deterministic benchmark fixtures.
- `TESTING_AND_QA.md` — unit/API/RAG/integration/E2E testing and release quality gates.
- `RISK_REGISTER.md` — active hackathon/product/security/integration risks and mitigations.
- `EXPERIMENT_BACKLOG.md` — hypotheses, experiments, metrics and validation tasks.

### Execution / delivery
- `ROADMAP_24H.md` — hour-by-hour hackathon execution plan and recovery rules.
- `DEPLOYMENT_OPERATIONS_AND_FALLBACKS.md` — live/demo modes, failure fallbacks, fresh-clone and deployment guidance.
- `DEMO_PITCH_AND_JUDGE_QA.md` — golden demo, pitch structure, objections and failure playbook.
- `PROMPT_LIBRARY.md` — reusable prompts for research, architecture, coding, evaluation, judging and integration.

## Handoff protocol

Every AI coding/research session should:

1. read the mandatory files above;
2. state the current objective;
3. verify whether the needed information already exists;
4. preserve working modules and shared contracts;
5. make only scoped changes;
6. test them;
7. give exact branch/commit/integration notes;
8. update `docs/PROJECT_STATUS.md`, `A_TO_Z_INDEX.md`, and/or `DECISION_LOG.md` when the project state materially changes.

For architecture or code-action work, also read:
- `SECURITY_AND_GUARDRAILS.md`
- `EVALUATION_FRAMEWORK.md`
- `RISK_REGISTER.md`

## Current strategic direction

The reference concept under investigation is an upgraded agentic software incident-response platform: ingest an incident/bug, understand it, collect evidence, find similar historical incidents, infer likely root cause, generate candidate remediation, score risk/confidence, request human approval when needed, execute a safe action (for example GitHub issue/PR or notification), verify the result, and store the learning for future incidents.

This is a direction, not a frozen final solution. The actual hackathon problem statement remains the primary constraint.

## Continuous research / completeness discipline

The recurring research loop should repeatedly:

1. audit `A_TO_Z_INDEX.md`;
2. determine what is already covered, outdated, contradictory, partial or waiting for PS;
3. inspect current first-party product/docs/research sources;
4. update this directory only when a finding materially changes understanding, design, benchmark, safety, product strategy or project description;
5. keep facts, measurements, hypotheses and future scope clearly separated.

Do not create thousands of meaningless pages just to increase document count. Prefer a large **high-signal** knowledge base over a larger pile of repetitive AI text. Growth is useful only when deduplicated, sourced, structured and reusable by teammates/coding agents.

## Current completeness rule

Anything dependent on the exact selected problem statement remains explicitly marked `WAITING_FOR_PS` rather than being invented. As soon as the PS is frozen, resolve those placeholders first before implementation begins.
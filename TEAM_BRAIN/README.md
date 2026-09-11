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

## Directory map

- `MASTER_PROMPT.md` — permanent project-wide AI operating prompt.
- `RESEARCH_LEDGER.md` — rolling research findings and market/problem observations.
- `PRODUCT_STRATEGY.md` — product thesis, users, workflow, moat and MVP/P1/P2 priorities.
- `COMPETITOR_GAPS.md` — what current incident-response / AI debugging products already do and where we should differentiate.
- `ARCHITECTURE_PLAYBOOK.md` — provisional target architecture, system boundaries and integration rules.
- `ARCHITECTURE_RESEARCH.md` — current architectural evidence, tradeoffs and lessons from the market/research ecosystem.
- `SECURITY_AND_GUARDRAILS.md` — autonomy boundaries, approval policy, Git/tool safety, prompt-injection handling and audit rules.
- `EVALUATION_FRAMEWORK.md` — benchmark design, metrics, regression gates and demo acceptance tests.
- `EXPERIMENT_BACKLOG.md` — hypotheses, experiments, metrics and validation tasks.
- `PROMPT_LIBRARY.md` — reusable prompts for research, architecture, coding, evaluation, judging and integration.
- `SOURCES.md` — evidence sources and links.
- `DECISION_LOG.md` — durable architecture/product decisions and their reasons.

## Handoff protocol

Every AI coding/research session should begin by reading:

1. `TEAM_BRAIN/README.md`
2. `docs/PROJECT_STATUS.md`
3. `TEAM_BRAIN/DECISION_LOG.md`
4. Relevant files in this directory
5. Existing code/contracts before proposing changes

For architecture or code-action work, also read:
- `TEAM_BRAIN/SECURITY_AND_GUARDRAILS.md`
- `TEAM_BRAIN/EVALUATION_FRAMEWORK.md`

Then the session should state the current objective, preserve working modules, make only scoped changes, test them, give the exact branch/commit message, and update the status/decision record when appropriate.

## Current strategic direction

The reference concept under investigation is an upgraded agentic software incident-response platform: ingest an incident/bug, understand it, collect evidence, find similar historical incidents, infer likely root cause, generate candidate remediation, score risk/confidence, request human approval when needed, execute a safe action (for example GitHub issue/PR or notification), verify the result, and store the learning for future incidents.

This is a direction, not a frozen final solution. The actual hackathon problem statement must remain the primary constraint.

## Continuous research discipline

The research loop should repeatedly inspect current first-party product/docs/research sources and update this directory only when a finding materially changes our understanding, design, benchmark, safety model or product strategy.

Do not create thousands of meaningless pages just to increase document count. Prefer a smaller, high-signal knowledge base that can actually be read by teammates and coding agents. Long-term growth is useful only when deduplicated, sourced and structured.

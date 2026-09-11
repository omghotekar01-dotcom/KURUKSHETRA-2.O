# KURUKSHETRA 2.0 — A-TO-Z PROJECT KNOWLEDGE INDEX

Last updated: 2026-09-11

Purpose: one canonical map of everything a teammate, ChatGPT, Codex, Astra, judge-prep session, or future maintainer must know to understand this project from zero.

Status meanings:
- **COVERED** — useful canonical information already exists.
- **PARTIAL** — useful information exists but needs more detail/evidence.
- **WAITING_FOR_PS** — cannot be truthfully finalized until the exact hackathon problem statement is frozen.
- **MISSING** — should be created as soon as practical.

Never duplicate a topic just because it appears in multiple places. Link to the authoritative file instead.

## A-to-Z completeness map

| Letter | Topic | Status | Canonical source |
|---|---|---|---|
| A | Architecture, agents, autonomy boundaries | COVERED | `ARCHITECTURE_PLAYBOOK.md`, `ARCHITECTURE_RESEARCH.md`, `SECURITY_AND_GUARDRAILS.md` |
| B | Business model, buyer, branch strategy | PARTIAL | `PRODUCT_STRATEGY.md`, `docs/TEAM_README.md`, `BUSINESS_STARTUP_AND_GTM.md` |
| C | Competitors, customers, contracts | COVERED/PARTIAL | `COMPETITOR_GAPS.md`, `PRODUCT_STRATEGY.md`, `DATA_API_AND_STATE_CONTRACTS.md` |
| D | Data, database, deployment, demo | PARTIAL | `DATA_API_AND_STATE_CONTRACTS.md`, `DEPLOYMENT_OPERATIONS_AND_FALLBACKS.md`, `DEMO_PITCH_AND_JUDGE_QA.md` |
| E | Event, evidence, evaluation | COVERED | `EVENT_AND_CONSTRAINTS.md`, `EVALUATION_FRAMEWORK.md`, `SOURCES.md` |
| F | Features, failure modes, fallbacks | COVERED/PARTIAL | `PRODUCT_STRATEGY.md`, `RISK_REGISTER.md`, `DEPLOYMENT_OPERATIONS_AND_FALLBACKS.md` |
| G | Git/GitHub, golden path, guardrails | COVERED | `docs/TEAM_README.md`, `MASTER_PROMPT.md`, `SECURITY_AND_GUARDRAILS.md` |
| H | Human-in-the-loop, handoff, history | COVERED | `SECURITY_AND_GUARDRAILS.md`, `docs/PROJECT_STATUS.md`, `DECISION_LOG.md` |
| I | Integrations, incident taxonomy | PARTIAL | `WORKFLOW_AND_AGENT_SPEC.md`, `INCIDENT_TAXONOMY_AND_TEST_SCENARIOS.md` |
| J | Judge strategy and objections | COVERED/PARTIAL | `DEMO_PITCH_AND_JUDGE_QA.md` |
| K | Knowledge base / RAG | COVERED/PARTIAL | `ARCHITECTURE_PLAYBOOK.md`, `RAG_AND_KNOWLEDGE_DESIGN.md`, `EVALUATION_FRAMEWORK.md` |
| L | LLM use, logging, latency | PARTIAL | `TECH_STACK_AND_DEPENDENCIES.md`, `NONFUNCTIONAL_REQUIREMENTS.md` |
| M | Metrics, market, MVP | COVERED | `PRODUCT_STRATEGY.md`, `EVALUATION_FRAMEWORK.md`, `BUSINESS_STARTUP_AND_GTM.md` |
| N | Novelty, non-functional requirements | COVERED/PARTIAL | `COMPETITOR_GAPS.md`, `NONFUNCTIONAL_REQUIREMENTS.md` |
| O | Observability, operations | PARTIAL | `DEPLOYMENT_OPERATIONS_AND_FALLBACKS.md`, `ARCHITECTURE_RESEARCH.md` |
| P | Problem, personas, prompts, privacy, pitch | PARTIAL / WAITING_FOR_PS | `CANONICAL_PROJECT_DESCRIPTION.md`, `PROBLEM_USERS_AND_PERSONAS.md`, `PROMPT_LIBRARY.md`, `SECURITY_AND_GUARDRAILS.md`, `DEMO_PITCH_AND_JUDGE_QA.md` |
| Q | Quality assurance | COVERED/PARTIAL | `EVALUATION_FRAMEWORK.md`, `TESTING_AND_QA.md` |
| R | Requirements, roadmap, research, risks | COVERED/PARTIAL | `REQUIREMENTS_CATALOG.md`, `ROADMAP_24H.md`, `RESEARCH_LEDGER.md`, `RISK_REGISTER.md` |
| S | Security, sources, scalability, startup | COVERED/PARTIAL | `SECURITY_AND_GUARDRAILS.md`, `SOURCES.md`, `BUSINESS_STARTUP_AND_GTM.md` |
| T | Tech stack, testing, timeline | COVERED/PARTIAL | `TECH_STACK_AND_DEPENDENCIES.md`, `TESTING_AND_QA.md`, `ROADMAP_24H.md` |
| U | UX/UI, users | PARTIAL | `UX_UI_SPEC.md`, `PROBLEM_USERS_AND_PERSONAS.md` |
| V | Verification, value proposition | COVERED | `EVALUATION_FRAMEWORK.md`, `PRODUCT_STRATEGY.md`, `WORKFLOW_AND_AGENT_SPEC.md` |
| W | Workflow, winning strategy | COVERED/PARTIAL | `WORKFLOW_AND_AGENT_SPEC.md`, `DEMO_PITCH_AND_JUDGE_QA.md`, `MASTER_PROMPT.md` |
| X | eXplainability, eXperiments | COVERED | `EXPERIMENT_BACKLOG.md`, `EVALUATION_FRAMEWORK.md`, `ARCHITECTURE_PLAYBOOK.md` |
| Y | Why-now / market timing / yield-impact story | PARTIAL | `BUSINESS_STARTUP_AND_GTM.md`, `RESEARCH_LEDGER.md` |
| Z | Zero-to-demo, zero-dependency fallback, final checklist | PARTIAL | `ROADMAP_24H.md`, `DEPLOYMENT_OPERATIONS_AND_FALLBACKS.md`, `DEMO_PITCH_AND_JUDGE_QA.md`, `docs/PROJECT_STATUS.md` |

## Information that must remain WAITING_FOR_PS until explicitly frozen

Do not invent these:

1. Exact problem statement text and ID.
2. Mandatory domain/technology constraints.
3. Exact final project name.
4. Final problem framing and judge rubric interpretation.
5. Final user/persona priority.
6. Final architecture and technology stack.
7. Final API/database contracts.
8. Final four-person task ownership.
9. Final feature scope and cut list.
10. Final demo story and measured numbers.

## Mandatory reading order for a new AI/team session

1. `TEAM_BRAIN/README.md`
2. `TEAM_BRAIN/A_TO_Z_INDEX.md`
3. `docs/PROJECT_STATUS.md`
4. `TEAM_BRAIN/EVENT_AND_CONSTRAINTS.md`
5. `TEAM_BRAIN/CANONICAL_PROJECT_DESCRIPTION.md`
6. `TEAM_BRAIN/DECISION_LOG.md`
7. Relevant architecture/product/security/evaluation file
8. Existing code/contracts before proposing edits

## Completeness rule

Every research/background run should first ask:

- Is the topic already covered?
- Is it current?
- Is it sourced?
- Does it contradict another file?
- Is it a fact, assumption, hypothesis, or decision?
- Does it change implementation, demo, evaluation, safety, or product strategy?

Only add information when the answer justifies an update.

## Current high-level completeness verdict

The repository now has strong coverage of research, architecture, safety, evaluation, product strategy, prompts and Git workflow. The main unresolved information is not missing due to neglect; it is intentionally waiting on the exact released problem statement. Once the PS is frozen, this index should be updated first and all WAITING_FOR_PS rows should be resolved into final project-specific specifications.
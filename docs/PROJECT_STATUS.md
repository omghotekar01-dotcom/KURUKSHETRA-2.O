# KURUKSHETRA 2.0 — LIVE PROJECT STATUS

> Source of truth for handoff between teammates, ChatGPT, Codex, Astra and other coding sessions.

## Last Updated

2026-09-11

## Current Phase

**RESEARCH / PRODUCT DISCOVERY / PRE-IMPLEMENTATION**

The repository collaboration workflow is established. Current effort is focused on problem/market research and evaluating an upgraded agentic engineering incident-response direction before the final architecture and individual work distribution are frozen.

## Repository State

- Repository: `omghotekar01-dotcom/KURUKSHETRA-2.O`
- Default branch: `main`
- Integration branch: `develop`
- `main` status: STABLE / MINIMAL
- `develop` status: ACTIVE
- Repository visibility: PUBLIC

## Completed

- [x] GitHub repository connected and verified
- [x] Write/admin access verified for the currently connected GitHub account
- [x] `main` identified as stable/default branch
- [x] `develop` integration branch created
- [x] Team collaboration/Git workflow guide added
- [x] Live project status tracker created
- [x] Four dedicated team branches exist: `OM-G`, `OM-PATIL`, `NIKHIL`, `YASH`
- [x] Initial reference project `Agentic-Bug-Router-and-Dispatcher` analyzed
- [x] Initial 2026 competitor/current-market research completed across AI SRE, AI debugging, incident response and coding agents
- [x] `TEAM_BRAIN/` research and prompt knowledge base initialized on `develop`
- [x] Project-wide master AI operating prompt created
- [x] Product strategy, competitor gap map and architecture playbook created
- [x] Experiment/evaluation backlog created
- [x] Reusable prompt library created
- [x] Primary source index created
- [x] Decision log initialized

## In Progress

- [ ] Continue current-market / research gap analysis
- [ ] Capture the exact Kurukshetra problem statement and constraints
- [ ] Decide GO / MODIFY / DROP for agentic incident-response direction against exact PS
- [ ] Finalize product wedge and one-sentence thesis
- [ ] Verify collaborator push/PR access from each teammate's machine

## Not Yet Frozen / Not Started

- [ ] Final solution definition
- [ ] Final MVP definition
- [ ] Final P0/P1/P2 feature classification
- [ ] Final technology stack selection
- [ ] Architecture freeze
- [ ] API contract
- [ ] Data/database contract
- [ ] Agent state/contracts
- [ ] Final repository code skeleton
- [ ] Work distribution among 4 members
- [ ] Implementation
- [ ] First integration
- [ ] Evaluation benchmark implementation
- [ ] End-to-end testing
- [ ] Demo preparation
- [ ] Final `develop` -> `main` release
- [ ] Fresh clone test
- [ ] Final submission/tag

## Active Branches

```text
main       -> stable/default/submission branch
develop    -> shared integration/research branch
OM-G       -> dedicated teammate branch
OM-PATIL   -> dedicated teammate branch
NIKHIL     -> dedicated teammate branch
YASH       -> dedicated teammate branch
```

Task ownership is not yet frozen. Do not infer permanent roles solely from branch names.

## TEAM_BRAIN Knowledge Base

Current files:

```text
TEAM_BRAIN/
├── README.md
├── MASTER_PROMPT.md
├── RESEARCH_LEDGER.md
├── PRODUCT_STRATEGY.md
├── COMPETITOR_GAPS.md
├── ARCHITECTURE_PLAYBOOK.md
├── EXPERIMENT_BACKLOG.md
├── PROMPT_LIBRARY.md
├── SOURCES.md
└── DECISION_LOG.md
```

All substantial ChatGPT/Codex/Astra research and development sessions should read these files before proposing major architecture changes.

## Current Product Direction (PROVISIONAL)

Investigating a startup-level agentic engineering incident-response system with a closed loop:

```text
Incident
→ Understand / route / prioritize
→ Gather code/history/runbook evidence
→ Rank root-cause hypotheses
→ Generate remediation
→ Score risk/confidence
→ Human approval when required
→ Bounded action (GitHub/notification/etc.)
→ Verification
→ Incident memory / learning
```

Potential differentiators currently under evaluation:

- evidence-backed multi-hypothesis RCA;
- structured incident memory;
- risk-aware action gate;
- remediation verification loop;
- GitHub-native lightweight workflow;
- visible evaluation/regression lab.

This direction is not final until aligned with the exact hackathon problem statement.

## Architecture

**PROVISIONAL RESEARCH ARCHITECTURE ONLY — NOT FROZEN.**

See `TEAM_BRAIN/ARCHITECTURE_PLAYBOOK.md`.

## Technology Stack

**PROVISIONAL — NOT FROZEN.**

Current likely direction:
- React + Vite + TypeScript;
- Tailwind/shadcn;
- FastAPI + Python + Pydantic + SQLAlchemy;
- PostgreSQL with SQLite/demo fallback;
- LangGraph;
- Groq/appropriate hosted LLM;
- Sentence Transformers + FAISS;
- GitHub API;
- MCP/direct integrations;
- Pytest + frontend/E2E tests.

## API Contract

**NOT YET FROZEN.**

## Database / Data Contract

**NOT YET FROZEN.**

## Known Risks / Blockers

1. Exact problem statement must determine final product scope.
2. Collaborator push/PR tests should be completed from all teammate machines.
3. Repository is public: nothing in `develop` or `TEAM_BRAIN/` is secret or hidden from someone who intentionally browses branches.
4. The AI incident-response market already contains strong products (Datadog, PagerDuty, Sentry, Rootly, incident.io, GitHub agents). Generic “AI bug router” positioning is insufficient.
5. Overbuilding observability infrastructure or autonomous production actions would be a poor 24-hour tradeoff.
6. External API/network dependence requires demo-mode fallbacks.

## Handoff Instructions for ChatGPT / Codex / Astra

Before making substantial changes:

1. Read `docs/TEAM_README.md`.
2. Read this `docs/PROJECT_STATUS.md`.
3. Read `TEAM_BRAIN/README.md` and `TEAM_BRAIN/DECISION_LOG.md`.
4. Read relevant strategy/research/prompt files.
5. Inspect current branches, code and latest commits.
6. Never overwrite working modules or casually restructure the repository.
7. Work on the correct dedicated/feature branch.
8. Explicitly flag breaking API/schema changes.
9. Update this status and/or decision log after meaningful milestones.

## Next Required Actions

1. Capture the exact PS.
2. Run the master PS evaluation and decide GO / MODIFY / DROP.
3. Freeze product thesis and P0 golden path.
4. Freeze architecture/contracts.
5. Assign exact work among four members and record ownership.
6. Create final code skeleton on `develop`, sync teammate branches, and begin parallel implementation.

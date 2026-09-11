# DECISION LOG

This file records durable project decisions. Do not rewrite history; append new decisions and mark old ones superseded when necessary.

## D-001 — Git workflow

Status: ACCEPTED

Decision:
- `main` = stable/submission branch.
- `develop` = integration branch.
- Dedicated teammate branches currently include `OM-G`, `OM-PATIL`, `NIKHIL`, `YASH`.
- Work merges into `develop` before final release to `main`.

Reason:
Protect stable code and allow parallel development without overwriting the project skeleton.

## D-002 — TEAM_BRAIN lives on develop during active research

Status: ACCEPTED

Decision:
Research/prompt/strategy files are maintained under `TEAM_BRAIN/` on `develop`.

Important limitation:
The repository is public. A file on `develop` is not secret; it is merely off the default branch.

## D-003 — Reference bug-router project is inspiration, not submission code

Status: ACCEPTED

Decision:
The public `Agentic-Bug-Router-and-Dispatcher` repository may inform architecture ideas, but we should not submit a lightly modified copy.

Reason:
The existing project is a small terminal proof-of-concept. Our final solution must be PS-aligned, independently architected and substantially differentiated.

## D-004 — Current product direction

Status: PROVISIONAL until exact PS is frozen

Decision:
Investigate an agentic engineering incident-response product centered on evidence-backed RCA, safe remediation, verification and incident memory.

Reason:
This direction has strong AI/automation/demo potential while leaving room for a startup-level workflow.

## D-005 — Avoid competing with enterprise observability on raw data ingestion

Status: ACCEPTED unless PS explicitly requires observability infrastructure

Decision:
Do not spend the hackathon rebuilding Datadog/Sentry/PagerDuty telemetry infrastructure.

Reason:
Mature platforms already dominate broad observability. Our wedge should be cross-context reasoning, trustworthy action and lightweight adoption.

## D-006 — Human approval remains authoritative for meaningful changes

Status: ACCEPTED

Decision:
AI may recommend and prepare actions, but MEDIUM/HIGH-risk actions require explicit human approval. AI must not self-approve and self-merge/deploy its own code.

Reason:
Safety, auditability and credible product design. It also aligns with modern coding-agent security practice.

## D-007 — Verification is separate from recommendation

Status: ACCEPTED

Decision:
A proposed remediation is not marked resolved until a verification step passes or a human explicitly resolves/escalates it.

Reason:
Prevents the product from becoming a polished recommendation generator with no closed loop.

## D-008 — Evaluation is a product feature, not only internal testing

Status: PROPOSED / HIGH PRIORITY

Decision:
Build a small Evaluation Lab/benchmark if time permits after golden-path stability.

Reason:
Agent quality can regress silently; visible evaluation demonstrates engineering maturity and creates a strong judge differentiator.

## D-009 — Default technical direction

Status: PROVISIONAL

Likely stack:
- React + Vite + TypeScript;
- Tailwind + shadcn/ui;
- FastAPI + Pydantic + SQLAlchemy;
- PostgreSQL with SQLite fallback;
- LangGraph;
- Groq/appropriate hosted LLM;
- Sentence Transformers + FAISS;
- GitHub API;
- MCP/direct integrations;
- Pytest + frontend/E2E tests.

This becomes final only after the exact PS and implementation plan are accepted.

## D-010 — Architecture must support degraded/demo mode

Status: ACCEPTED

Decision:
External LLM, GitHub, Gmail/Slack or remote database failure must not make the entire demo unusable.

Reason:
Hackathon network/API failures are predictable risks.

## D-011 — Local launcher must recover from backend port collisions

Status: ACCEPTED

Decision:
The one-command launcher selects the first free backend port in `8000–8099`, injects that exact API base into the Vite process, and keeps the browser-facing development origin on `http://localhost:5173`. If frontend port 5173 is occupied, startup fails clearly instead of silently reusing an unrelated service.

Reason:
A hackathon laptop can already have another API on port 8000. Reusing an unknown service caused the dashboard to surface `Failed to fetch`; choosing a free backend port while preserving the trusted frontend origin makes the startup path deterministic and avoids misleading cross-origin failures.

Consequences:
- Backend URLs printed by the launcher may use a port other than 8000.
- `.run/backend.port` records the selected backend port for operator diagnostics.
- The launcher does not treat an arbitrary listener on 5173 as this project.

Date: 2026-09-11

## D-012 — CI derives verification evidence but cannot prove runtime recovery

Status: ACCEPTED

Decision:
Real GitHub Actions/check state is converted into canonical incident-verification evidence. Failed CI may derive a failed verification outcome and escalate the incident automatically. Pending or absent checks remain inconclusive. Passing CI remains evidence-only and must not automatically resolve the incident; human/runtime confirmation is still required.

Reason:
A green build proves the configured checks passed on the isolated remediation commit. It does not prove the original production symptom, dependency, environment or user workflow recovered. Treating CI success as automatic incident resolution would create a false closed loop.

Consequences:
- `PATCH_CI_VERIFICATION` stores observed GitHub state plus derived evidence.
- `VERIFICATION_DERIVED` makes that derivation auditable in the incident timeline.
- CI failure can safely move the incident to escalation without waiting for manual confirmation.
- CI success keeps the incident in `VERIFYING` until runtime/human evidence is supplied.

Date: 2026-09-11

---

## Decision template

### D-XXX — Title

Status: PROPOSED / ACCEPTED / SUPERSEDED / REJECTED

Decision:
...

Reason:
...

Alternatives considered:
...

Consequences:
...

Date:
...

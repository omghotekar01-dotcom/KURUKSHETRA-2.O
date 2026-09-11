# Implementation Progress

Last updated: 2026-09-11
Active build branch: `agent-build-core`
Draft integration PR: `#1` → `develop`

## Build principle

Move from the documented architecture to a reliable end-to-end product in small, testable milestones. `main` remains untouched until the integrated build is reviewed.

## Completed

### Foundation
- Created dedicated implementation branch from `develop`.
- Added secret-safe `.gitignore` and `.env.example`.
- Added FastAPI/Pydantic backend foundation.
- Added deterministic triage fallback for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
- Added deterministic action-risk policy with LOW/MEDIUM/HIGH consequence classes.
- Added API endpoints for health, standalone triage and action-risk evaluation.
- Added responsive React/Vite incident-command dashboard shell.

### Persistent incident lifecycle
- Added SQLite-backed incident repository with zero extra runtime dependencies.
- Added persistent incident IDs, timestamps, lifecycle state and audit timeline events.
- Added create/list/detail incident APIs.
- Connected the frontend incident intake form to the backend create API.
- Added recent-incident sidebar data from the API.
- Added environment variables for local API/database configuration.

### Historical evidence retrieval
- Added curated demo runbook corpus covering authentication, database, backend, frontend and infrastructure incidents.
- Added deterministic lexical/cosine retrieval baseline.
- Added no-strong-match behavior instead of forcing a historical fix.
- Added incident investigation endpoint and evidence timeline events.
- Added UI cards for historical matches with source score and known response.

### RCA and remediation baseline
- Added structured evidence bundle, root-cause hypothesis and remediation schemas.
- Added deterministic evidence-backed RCA baseline using the strongest retrieved runbook evidence.
- Added explicit next-diagnostic guidance.
- Added remediation plan + verification plan generation.
- Routed proposed remediation through the deterministic risk policy.
- Added `REMEDIATION_READY` and escalation workflow transitions.
- Added analysis endpoint and timeline events for RCA/remediation.
- Added UI panels for top hypothesis, confidence, next diagnostic, remediation, risk policy and verification plan.

### Approval, bounded action and verification
- Added explicit `APPROVE` / `REJECT` contracts tied to the exact proposed action.
- Server re-evaluates action risk at approval time rather than trusting UI state.
- High-risk actions remain blocked even when a reviewer clicks approve.
- Added bounded execution adapter with honest `DEMO/SIMULATED` semantics; it never pretends an external provider changed state.
- Added `VERIFYING`, `RESOLVED` and escalation transitions.
- Added `PASS` / `FAIL` / `INCONCLUSIVE` verification endpoint.
- Added approval, action and verification events to the audit timeline.
- Added dashboard approval/reject controls, action-result card and verification controls.

### Continuous integration
- Added GitHub Actions backend compile/test job and frontend TypeScript/Vite build job.
- First CI run correctly exposed a Python import-path issue and obsolete TypeScript module resolver.
- Fixed CI to run tests via `python -m pytest` and switched TypeScript to Vite-compatible `moduleResolution: Bundler`.
- Added `vite-env.d.ts` and a strict TypeScript no-emit check before Vite build.

## Tests actually executed

Latest GitHub Actions run on the full branch:

```text
Backend compile: PASS
Backend tests:   18 passed, 2 dependency deprecation warnings, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite build: PASS
Overall workflow: SUCCESS
```

The warnings are from upstream Starlette/FastAPI test-client dependencies, not application test failures.

Additional local smoke validation of the new closed-loop path:

```text
2 passed in 0.36s
python -m compileall -q app tests -> PASS
```

Covered behavior now includes:
- Authentication triage.
- Unclassified/low-confidence triage.
- Low-risk action policy.
- Blocked high-risk production action.
- SQLite incident persistence.
- Incident timeline persistence.
- Create/list/get incident APIs.
- 404 behavior for missing incident.
- JWT runbook retrieval.
- No-match retrieval behavior.
- Investigation API evidence flow.
- RCA/remediation generation.
- No-match human-escalation path.
- Analysis API workflow and `REMEDIATION_READY` transition.
- Human approve/reject path.
- Simulated bounded execution.
- High-risk action blocking after approval.
- Verification pass → `RESOLVED`.

## Current P0 sequence

1. ~~Connect incident intake UI to backend triage API.~~
2. ~~Add incident persistence and timeline state.~~
3. ~~Add local historical/runbook corpus and retrieval baseline.~~
4. ~~Add evidence objects and ranked RCA hypothesis baseline.~~
5. ~~Add remediation + deterministic risk gate to incident workflow.~~
6. ~~Add explicit approval event and bounded action adapter.~~
7. ~~Add verification result and resolution transition.~~
8. Add structured resolution memory + deterministic demo fixtures/fallback switch.
9. Add evaluation runner and judge-facing scorecard.
10. Add optional bounded GitHub issue adapter when credentials/controlled target are configured.
11. Run clean-clone/setup acceptance test, polish UX, then move draft PR toward review.

## Next highest-value milestone

Persist verified resolution memory and make it reusable by future incidents:

```text
VERIFICATION PASS
→ structured memory record
→ symptoms + component + actual/working root cause
→ approved action
→ verification evidence
→ reusable retrieval candidate
```

Then add deterministic evaluation fixtures so routing, retrieval, RCA, policy and verification can be scored in a repeatable judge-facing benchmark.

## Known implementation risks

- Exact PS-specific requirements still override generic assumptions if they differ from the current direction.
- Current retrieval/RCA is deliberately deterministic and lightweight; embedding/LLM upgrades must beat the baseline in evaluation before replacing it.
- Real external integrations must never silently fall back from failure to a fake success state.
- The frontend currently uses package versions resolved at install time; a lockfile should be committed once dependency versions are stabilized.
- The repository is public; no secrets or private operational data may be committed.

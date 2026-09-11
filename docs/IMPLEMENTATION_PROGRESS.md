# Implementation Progress

Last updated: 2026-09-11
Active build branch: `agent-build-core`
Draft integration PR: `#1` → `develop`

## Build principle

Build a real, live-first MVP in small, runnable, testable milestones. Emergency demo mode exists only as a fallback. `main` remains untouched until the integrated build is reviewed.

## Completed

### Foundation
- FastAPI/Pydantic backend and React/Vite/TypeScript frontend.
- Deterministic triage baseline for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
- Deterministic LOW/MEDIUM/HIGH action-risk policy.
- Responsive dashboard with Light theme as default and persistent Light/Dark switcher.
- API-first structure so the backend can later serve web, PWA/mobile or desktop clients.

### Persistent incident lifecycle
- SQLite-backed incident store with IDs, timestamps, lifecycle state and auditable timeline events.
- Create/list/detail incident APIs and recent-incidents UI.
- Incident states through investigation, remediation, approval, execution, verification, resolution and escalation.

### Evidence, RCA and remediation
- Curated local runbook/knowledge corpus and deterministic retrieval baseline.
- Verified resolution memory participates in later retrieval.
- No-strong-match behavior instead of forcing a historical fix.
- Evidence bundle, ranked RCA hypothesis, confidence, next diagnostic, remediation and verification plan.
- Human escalation when neither historical nor repository evidence is strong enough.

### Live GitHub repository investigation
- Added real read-only GitHub context collection for an allowlisted repository.
- Reads repository metadata, recent commits, commit details, changed files and open issues from GitHub.
- Ranks recent commits using a deterministic incident-correlation signal based on incident text/logs/triage versus commit messages and filenames.
- Correlation is explicitly presented as investigation guidance, not proof of causation.
- Live repository evidence is attached to RCA and stored in the incident timeline as `REPOSITORY_EVIDENCE`.
- A provider/policy failure records `REPOSITORY_CONTEXT_UNAVAILABLE`; the system does not fabricate repository evidence.
- Added `GET /api/v1/incidents/{incident_id}/repository-context`.
- Dashboard now shows repository, default branch, access mode, correlated commits, changed files and open issues with real links.

### Live diff/hunk investigation
- GitHub commit inspection now consumes real patch text returned for changed files when available.
- Unified diff hunks are parsed into bounded evidence objects containing file, hunk header, added lines, removed lines and matched incident terms.
- Code-aware tokenization splits paths and snake_case identifiers, so incident terms such as `jwt` can match `auth/jwt.py` and `jwt_signing_key`.
- Each hunk receives an incident-correlation score and the strongest hunks contribute to commit ranking.
- RCA now cites the top live diff hunk when it crosses the evidence threshold and tells the operator exactly which file/hunk to inspect next.
- Missing GitHub patch text for binary/very-large diffs is treated as unavailable evidence and is never fabricated.
- Diff correlation remains a prioritization signal, not a declaration that the code is faulty.

### Human approval and real bounded GitHub action
- Explicit `APPROVE` / `REJECT` contracts tied to the exact proposed action.
- Server re-evaluates action risk at approval time rather than trusting UI state.
- High-risk operations such as deploy/merge/destructive production actions remain blocked/recommendation-only.
- Medium-risk GitHub issue creation requires human approval.
- After approval, the live adapter can create a real GitHub Issue in an allowlisted repository using `GITHUB_TOKEN` or authenticated GitHub CLI credentials.
- Successful action returns `EXECUTED`, `GITHUB` and the real GitHub URL.
- Missing credentials return `AUTH_REQUIRED`, `LIVE`; provider errors return `FAILED`; neither path is presented as success.
- Only real `EXECUTED` (or explicit emergency `SIMULATED`) action results advance to verification.

### Verification and verified resolution memory
- `PASS` / `FAIL` / `INCONCLUSIVE` verification endpoint and UI.
- PASS marks incident `RESOLVED`; failed/inconclusive verification escalates.
- PASS stores symptoms, component, severity, working RCA, approved remediation and verification evidence in reusable resolution memory.
- Added `/api/v1/memory`.

### Emergency deterministic fallback
- Version-controlled demo fixtures remain available for internet/provider failure.
- `DEMO_MODE` defaults to `false`; the product path is live-first.
- Demo execution remains clearly labelled `SIMULATED/DEMO` and is never confused with a live provider action.

### Continuous integration
- GitHub Actions compiles/tests backend and builds the TypeScript/Vite frontend on every branch/PR update.
- CI has caught real regressions during development, including import-path, TypeScript resolver, stale policy expectation, icon-export and diff-tokenization test failures; each was fixed before handoff.

## Latest confirmed validation

GitHub Actions run on head `77bc2f072be50b3ef82b1840256d7d1bb62cf3b1` is green:

```text
Backend compile: PASS
Backend tests:   29 passed, 2 dependency deprecation warnings, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite build: PASS
Overall: SUCCESS
```

Confirmed coverage includes:
- triage and unknown/low-confidence paths
- risk policy and high-risk blocking
- SQLite persistence and timeline
- create/list/get APIs and 404s
- historical retrieval/no-match handling
- RCA/remediation workflow
- approve/reject path
- live GitHub issue execution contract
- missing-auth fail-closed behavior
- verification → resolution/escalation
- verified incident memory
- GitHub repository allowlist rejection
- live GitHub repository context mapping/correlation/open-issue filtering
- real patch parsing and diff-hunk correlation
- code-identifier tokenization for incident matching
- repository and diff evidence included in RCA
- frontend production build

## Current live MVP path

```text
Incident + repository
→ Persist + triage
→ Historical knowledge retrieval
→ Live GitHub repository investigation
→ Real commit + changed-file + diff-hunk evidence
→ Evidence-backed RCA
→ Remediation + deterministic risk gate
→ Human approval
→ Real allowlisted GitHub issue creation
→ Verification
→ Resolved / Escalated
→ Verified resolution memory
```

## Current P0 sequence

1. ~~Incident intake + triage.~~
2. ~~Persistence + audit timeline.~~
3. ~~Historical knowledge retrieval.~~
4. ~~Evidence-backed RCA baseline.~~
5. ~~Remediation + deterministic risk gate.~~
6. ~~Explicit human approval.~~
7. ~~Verification + resolution transition.~~
8. ~~Structured verified-resolution memory.~~
9. ~~Emergency deterministic fallback.~~
10. ~~Real bounded GitHub issue action.~~
11. ~~Live GitHub repository metadata/commit/file/issue investigation.~~
12. ~~Real diff parsing + suspicious-hunk ranking + RCA grounding.~~
13. Surface ranked hunks cleanly in the dashboard and add surrounding source-context inspection.
14. Add bounded patch proposal, branch + draft PR workflow behind approval.
15. Add automated test/CI verification of the proposed patch.
16. Add evaluation runner + judge-facing scorecard.
17. Lock frontend dependencies, run clean-clone acceptance, polish UX and move PR toward review.

## Next highest-value milestone

Turn the backend diff evidence into an operator-grade diagnosis surface and patch proposal pipeline:

```text
Live incident
→ ranked commit
→ ranked diff hunk
→ fetch surrounding source context
→ explain why the exact change is suspicious
→ prepare smallest bounded patch proposal
→ human reviews exact diff
→ no repository write until approval
```

After that, the approved patch workflow will create an isolated fix branch, run tests/build checks and create a DRAFT PR only if verification passes. No automatic merge or production deployment.

## Known implementation risks

- Exact hackathon PS requirements override generic assumptions if they differ from this direction.
- Commit and diff-hunk correlation are deterministic heuristics; they guide investigation and do not establish causal proof.
- Current historical retrieval/RCA is lightweight; any embedding/LLM upgrade must beat the deterministic baseline in evaluation before replacing it.
- GitHub public API rate limits and network availability can affect live context retrieval; emergency fallback remains available.
- GitHub can omit patch text for binary or large diffs; unavailable patch evidence must remain explicitly unavailable.
- Real external integrations must never silently fall back to fake success.
- No automatic merge, production deployment, destructive database operation or unrestricted repository write is permitted in the MVP.
- The public repository must never contain tokens, credentials or private operational data.

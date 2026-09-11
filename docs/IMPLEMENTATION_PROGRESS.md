# Implementation Progress

Last updated: 2026-09-11
Active build branch: `agent-build-core`
Draft integration PR: `#1` → `develop`

## Build principle

Build a real, live-first MVP in small, runnable, testable milestones. Emergency demo mode exists only as a fallback. `main` remains untouched until the integrated build is reviewed.

## Completed

### Foundation
- FastAPI/Pydantic backend and React/Vite/TypeScript frontend.
- Deterministic triage for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
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
- Real read-only GitHub context collection for an allowlisted repository.
- Reads repository metadata, recent commits, commit details, changed files and open issues.
- Ranks recent commits using incident text/logs/triage versus commit messages and filenames.
- Correlation is investigation guidance, not proof of causation.
- Repository evidence is attached to RCA and stored as `REPOSITORY_EVIDENCE`.
- Provider/policy failure records `REPOSITORY_CONTEXT_UNAVAILABLE`; evidence is never fabricated.
- Added `GET /api/v1/incidents/{incident_id}/repository-context`.

### Live diff, hunk and bounded source-context diagnosis
- Consumes real patch text returned by GitHub for changed files when available.
- Parses unified diff hunks into typed evidence: filename, hunk header, added/removed lines, matched terms and correlation score.
- Code-aware tokenization splits paths/snake_case so incident signals such as `jwt` match identifiers such as `jwt_signing_key`.
- Strongest hunks contribute to commit ranking and RCA evidence.
- RCA identifies the exact file/hunk to inspect next without declaring it faulty.
- For the top two hunks of the top-ranked commit, the backend performs bounded read-only source retrieval at that exact commit SHA and returns line-numbered surrounding context.
- Binary/very-large/missing patch or source data remains explicitly unavailable; nothing is invented.
- Dedicated `/evidence` UI provides a judge/operator-friendly live evidence lab with correlated commits, changed files, ranked hunks, removed/added lines, matched symptom terms, bounded source context and real GitHub links.
- The main application now exposes a one-click `Live Evidence Lab` shortcut.

### Human approval and real bounded GitHub action
- Explicit `APPROVE` / `REJECT` contracts tied to the exact proposed action.
- Server re-evaluates action risk at approval time rather than trusting UI state.
- High-risk deploy/merge/destructive production operations remain blocked/recommendation-only.
- Medium-risk GitHub issue creation requires human approval.
- After approval, the live adapter can create a real GitHub Issue in an allowlisted repository using `GITHUB_TOKEN` or authenticated GitHub CLI credentials.
- Success returns `EXECUTED`, `GITHUB` and the real URL.
- Missing credentials return `AUTH_REQUIRED`, provider failures return `FAILED`; neither is presented as success.

### Verification and verified-resolution memory
- `PASS` / `FAIL` / `INCONCLUSIVE` verification endpoint and UI.
- PASS marks incident `RESOLVED`; failed/inconclusive verification escalates.
- PASS stores symptoms, component, severity, working RCA, approved remediation and verification evidence for future retrieval.
- Added `/api/v1/memory`.

### Emergency fallback
- Version-controlled demo fixtures remain available for internet/provider failure.
- `DEMO_MODE` defaults to `false`; the normal product path is live-first.
- Fallback execution remains visibly `SIMULATED/DEMO` and is never confused with live success.

### Continuous integration
- GitHub Actions compiles/tests backend and builds the TypeScript/Vite frontend on every branch/PR update.
- CI has caught real regressions during development, including Python import path, TypeScript resolver, stale policy expectation, icon export and code-tokenization issues; regressions were fixed before handoff.

## Latest confirmed validation

GitHub Actions run #134 on head `e30cc1f9667db89f7a57514ac70bd692e0520e72` is fully green:

```text
Backend compile: PASS
Backend tests:   29 passed, 2 dependency deprecation warnings, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite production build: PASS
Overall workflow: SUCCESS
```

Confirmed coverage includes triage, risk policy, SQLite persistence, historical retrieval, RCA/remediation, approval/rejection, live GitHub issue action contract, missing-auth fail-closed behavior, verification/resolution memory, repository allowlist enforcement, live GitHub repository context, real patch parsing, suspicious-hunk ranking, code-aware symptom matching, bounded source context, RCA evidence grounding and frontend production build.

## Current live MVP path

```text
Incident + repository
→ Persist + triage
→ Historical knowledge retrieval
→ Live GitHub repository investigation
→ Real commit + changed-file evidence
→ Real ranked diff hunks
→ Bounded source context at exact commit
→ Evidence-backed RCA
→ Remediation + deterministic risk gate
→ Human approval
→ Real allowlisted GitHub issue creation
→ Verification
→ Resolved / Escalated
→ Verified resolution memory
```

## P0 sequence

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
13. ~~Operator-grade Evidence Lab + bounded source-context inspection.~~
14. Add an exact bounded patch proposal that is reviewable before any write.
15. After explicit approval only: create isolated fix branch, apply approved patch and run tests/build.
16. Create a DRAFT PR only if checks pass; never auto-merge.
17. Derive verification from real test/CI results.
18. Add evaluation runner + judge-facing scorecard.
19. Lock dependencies, run clean-clone acceptance, finish UX/docs/recovery polish.

## Next highest-value milestone

Patch proposal without silent mutation:

```text
Live incident
→ ranked commit/hunk/source context
→ prepare smallest exact patch proposal
→ show before/after diff + rationale + confidence + verification commands
→ human approves or rejects exact proposal
→ no branch/file write before approval
```

The following milestone will take an approved proposal, create an isolated fix branch, apply only that approved change, run deterministic checks and create a DRAFT PR only when checks pass. Automatic merge or production deployment is explicitly out of scope.

## Known implementation risks

- Exact hackathon PS requirements override generic assumptions if they differ from this direction.
- Commit/hunk correlation is heuristic investigation guidance, not causal proof.
- GitHub API rate limits/network availability may affect live evidence; emergency fallback remains available.
- GitHub may omit patch/content data for binary or large files; unavailable evidence remains unavailable.
- Real integrations must never silently degrade to fake success.
- No automatic merge, production deployment, destructive database operation or unrestricted repository write is permitted.
- The public repository must never contain tokens, credentials or private operational data.

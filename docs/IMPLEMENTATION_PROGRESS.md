# Implementation Progress

Last updated: 2026-09-11
Active build branch: `agent-build-core`
Draft integration PR: `#1` → `develop`
Project name: **AI Agentic Bug Router**

## Build principle

Build a real, live-first MVP in small, runnable, testable milestones. Emergency demo mode exists only as a fallback. `main` remains untouched until the integrated build is reviewed.

## Completed

### Foundation
- FastAPI/Pydantic backend and React/Vite/TypeScript frontend.
- Deterministic triage for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
- Deterministic LOW/MEDIUM/HIGH action-risk policy.
- Responsive dashboard with Light theme as default and persistent Light/Dark switcher.
- API-first structure so the same backend can later serve web, PWA/mobile or desktop clients.

### Persistent incident lifecycle
- SQLite-backed incident store with IDs, timestamps, lifecycle state and auditable timeline events.
- Create/list/detail incident APIs and recent-incidents UI.
- Incident states through investigation, remediation, approval, execution, verification, resolution and escalation.

### Evidence, RCA and routing
- Curated local runbook/knowledge corpus and deterministic retrieval baseline.
- Verified resolution memory participates in later retrieval.
- No-strong-match behavior instead of forcing a historical fix.
- Evidence bundle, ranked RCA hypothesis, confidence, next diagnostic, remediation and verification plan.
- Human escalation when neither historical nor repository evidence is strong enough.

### Live GitHub repository investigation
- Real read-only GitHub context collection for an allowlisted repository.
- Reads repository metadata, recent commits, commit details, changed files and open issues.
- Ranks recent commits using incident text/logs/triage versus commit messages and filenames.
- Consumes real unified diff patches when GitHub exposes them.
- Parses and ranks suspicious hunks using code-aware incident-term correlation.
- Fetches bounded source context at the exact commit SHA for strongest hunks.
- Dedicated `/evidence` UI exposes correlated commits, changed files, ranked hunks, source context and real GitHub links.
- Correlation is explicitly investigation guidance, not proof of causation.

### Exact bounded patch proposal
- `POST /api/v1/incidents/{incident_id}/patch-proposal` creates a reviewable candidate without writing to GitHub.
- Proposal generation revalidates the selected commit/hunk against fresh live evidence.
- Current strategy is a conservative `REVERT_SUSPICIOUS_HUNK` candidate only when the exact added-line sequence still exists.
- Stale, ambiguous or missing source evidence fails closed instead of inventing a patch.
- Proposal contains exact file, base commit, line start, current lines, replacement lines, diff preview, rationale, confidence and required validation commands.

### Approval-gated live remediation
- Dedicated `/remediate` Remediation Studio.
- Human can explicitly APPROVE or REJECT the exact reviewed patch proposal.
- Approval re-fetches live evidence and requires the proposal ID, commit, file, hunk, before-lines and after-lines to still match exactly.
- Before a write, the current default-branch file is re-read; missing or ambiguous target sequences fail closed.
- Approved changes are isolated on deterministic `incident-fix/...` branches.
- Only the exact approved sequence is replaced.
- Branch content is re-read after the write to verify patch integrity.
- Frontend changes run dependency install + production build in a fresh clone.
- Backend/Python changes run compile + pytest in a fresh clone.
- Documentation-only changes use exact content-integrity validation.
- Unknown executable code types fail closed until a trusted deterministic validator exists.
- A **Draft PR** is created only after configured validation passes.
- No automatic merge or deployment exists.

### Retry-safe remediation and idempotency
- Exact incident + patch proposal receives a deterministic `REM-...` idempotency key.
- Same-proposal approval requests are serialized with a per-key lock in the current API process.
- Completed successful remediation is returned from the audit timeline instead of creating a second GitHub write.
- Deterministic fix branches replace timestamp-suffixed duplicate branches.
- A retry can safely resume a branch that was created but not yet patched when its base/content still match exactly.
- A retry reuses an already-patched exact branch without rewriting it.
- Any existing deterministic branch with conflicting content fails closed.
- Existing open PR for the deterministic remediation branch is reused instead of duplicated.
- A matching closed PR blocks automatic recreation and requires review.
- Audit metadata stores idempotency key, branch, branch URL, commit, PR, validation and reuse state.
- Duplicate successful approvals record `PATCH_EXECUTION_REUSED`.

### Live GitHub CI verification
- Build workflow also runs on `incident-fix/**` pushes and PRs targeting `main` or `develop`.
- `GET /api/v1/incidents/{incident_id}/patch-verification` reads the actual Draft PR, remediation commit, GitHub check-runs and combined status.
- CI state is derived as `PASS`, `FAIL`, `PENDING` or `NO_CHECKS`; absence of checks is never treated as success.
- Failing GitHub checks escalate the incident; passing checks keep the incident in `VERIFYING` because merge/runtime verification still belongs to a human.
- Remediation Studio exposes a live CI status panel with direct check links.
- CI state changes are recorded as `PATCH_CI_VERIFICATION` timeline events without duplicating identical poll results.

### Measured Evaluation Lab
- Added versioned deterministic benchmark `2026.09.11-v1` and `GET /api/v1/evaluation/run`.
- Benchmark exercises five routing domains: Authentication, Database, Backend, Frontend and Infrastructure.
- Measures routing accuracy, expected evidence retrieval, RCA evidence grounding, intentional no-match escalation, risk-policy accuracy, unsafe-action blocking and approval-gate correctness.
- The unknown-service case must remain unmatched and escalate instead of forcing a confident diagnosis.
- High-risk production/destructive benchmark actions must remain `RECOMMENDATION_ONLY`.
- Every score is computed from the current backend functions when the benchmark runs; no metric value is hard-coded into the frontend.
- Dedicated `/evaluation` judge-facing Light-theme scorecard exposes metric numerators/denominators, every PASS/FAIL case, expected vs observed behavior, benchmark version/time, rerun control and truth-boundary notes.
- The displayed overall score is only the simple mean of the shown deterministic metric ratios; it is explicitly not presented as an industry-wide accuracy claim.

### Other bounded GitHub action
- Medium-risk GitHub issue creation requires human approval.
- Missing credentials return `AUTH_REQUIRED`; provider failures return `FAILED`; neither is presented as success.

### Verification and verified-resolution memory
- `PASS` / `FAIL` / `INCONCLUSIVE` verification endpoint and UI.
- PASS marks an incident `RESOLVED`; failed/inconclusive verification escalates.
- Verified resolution stores symptoms, component, severity, working RCA, approved remediation and evidence for future retrieval.

### Emergency fallback
- Version-controlled demo fixtures remain available for internet/provider failure.
- `DEMO_MODE` defaults to `false`; the normal product path is live-first.
- Fallback execution remains visibly `SIMULATED/DEMO` and is never confused with live success.

## Latest confirmed validation

GitHub Actions run #240 on implementation head `efe41371178733c0a1867aa243ba8d83e12968ea` completed successfully:

```text
Backend compile: PASS
Backend tests:   51 passed, 2 dependency deprecation warnings, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite production build: PASS
Overall workflow: SUCCESS
```

Confirmed coverage includes deterministic remediation identity, completed-execution reuse, deterministic branch naming, fresh branch re-read after creation, interrupted/retry-safe branch recovery, existing branch/PR reuse with zero extra writes, plus the existing triage, risk, persistence, retrieval, RCA, repository evidence, patch proposal, stale-write rejection, CI verification, Evaluation Lab and verified-memory coverage.

## Current live MVP path

```text
Incident + repository
→ Persist + triage / route
→ Historical knowledge retrieval
→ Live GitHub repository investigation
→ Real commits + changed files + diff hunks
→ Bounded source context
→ Evidence-backed RCA
→ Exact patch proposal (NO WRITE)
→ Human APPROVE / REJECT
→ Stable remediation idempotency key
→ Fresh proposal + file revalidation
→ Deterministic isolated incident-fix branch
→ Apply only approved replacement OR safely reuse exact retry state
→ Local deterministic validation
→ Draft PR only if green OR reuse existing exact open PR
→ Live GitHub CI verification
→ Human review / runtime verification
→ Resolved or escalated
→ Verified resolution memory

Parallel proof surface:
Versioned benchmark → measured routing/retrieval/RCA/safety metrics → judge-facing Evaluation Lab
```

## P0 sequence

1. ~~Incident intake + triage/routing.~~
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
14. ~~Exact bounded patch proposal reviewable before any repository write.~~
15. ~~Approval-gated isolated fix branch + exact patch application + deterministic validation.~~
16. ~~Draft PR only after validation; never auto-merge.~~
17. ~~Derive remediation verification from real GitHub CI/check state.~~
18. ~~Repeatable Evaluation Lab + judge-facing measured scorecard.~~
19. ~~Remediation idempotency and retry-safe branch/PR reuse.~~
20. Lock dependencies and add clean-clone / one-command acceptance workflow.
21. Final responsive Light-theme polish, documentation, demo recovery and security pass.

## Next highest-value milestone

Reproducible startup and clean-clone acceptance before demo freeze:

```text
dependency pinning / lock strategy
→ environment preflight
→ one-command Windows startup
→ one-command Unix startup
→ backend health wait
→ frontend startup
→ clean-clone smoke test
→ clear failure diagnostics
```

After that, finish judge-facing UX/recovery/security polish without changing the trusted golden path.

## Known implementation risks

- Exact hackathon problem-statement constraints override generic assumptions if they differ from this direction.
- Commit/hunk correlation is heuristic investigation guidance, not causal proof.
- The current patch strategy is a conservative hunk-revert candidate, not a guarantee of the best semantic fix.
- The current benchmark is intentionally small and deterministic; a perfect score on it is not a claim of general real-world accuracy.
- GitHub API rate limits/network availability may affect live evidence or check polling.
- GitHub may omit patch/content data for binary or large files; unavailable evidence remains unavailable.
- In-process approval serialization protects the current single-API-process MVP; a future horizontally scaled deployment should use a shared/distributed idempotency store or database constraint.
- Passing CI proves configured checks passed; it does not prove production recovery or justify automatic merge.
- Real integrations must never silently degrade to fake success.
- No automatic merge, production deployment, destructive database operation or unrestricted repository write is permitted.
- The public repository must never contain tokens, credentials or private operational data.

# Implementation Progress

Last updated: 2026-09-11  
Active build branch: `agent-build-core`  
Draft integration PR: `#1` → `develop`  
Project name: **AI Agentic Bug Router**

## Build principle

Build a real, live-first MVP in small, runnable, testable milestones. Emergency demo mode exists only as a visibly labeled fallback. `main` remains untouched until the final reviewed release candidate is ready.

## Completed live MVP

### Foundation and incident lifecycle
- FastAPI/Pydantic backend + React/Vite/TypeScript frontend.
- SQLite-backed incident persistence, IDs, lifecycle state and auditable timeline.
- Deterministic triage for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
- Deterministic LOW/MEDIUM/HIGH action-risk policy.
- Responsive Light-theme-first UI with persistent Light/Dark switcher.

### Evidence, routing and RCA
- Curated local runbook/knowledge retrieval baseline.
- Verified resolution memory participates in later retrieval.
- No-strong-match behavior instead of forced historical answers.
- Evidence-backed RCA hypothesis, confidence, next diagnostic, remediation and verification plan.
- Human escalation when evidence is insufficient.

### Live GitHub investigation
- Read-only GitHub context for an allowlisted repository.
- Reads repository metadata, recent commits, commit details, changed files and open issues.
- Uses real unified-diff patches when GitHub exposes them.
- Parses and ranks suspicious hunks using incident/code token correlation.
- Fetches bounded source context at the exact commit SHA for top hunks.
- `/evidence` exposes correlated commits, changed files, ranked hunks, source context and GitHub links.
- Correlation is explicitly investigation guidance, not proof of causation.

### Exact bounded patch proposal
- `POST /api/v1/incidents/{incident_id}/patch-proposal` creates a reviewable candidate with **no repository write**.
- Proposal generation revalidates the selected live commit/hunk.
- Current conservative strategy is `REVERT_SUSPICIOUS_HUNK` only when the exact added-line sequence still exists.
- Stale, ambiguous or missing source evidence fails closed.
- Proposal contains exact file, base commit, hunk, before/after lines, diff preview, rationale, confidence, warnings and verification commands.

### Approval-gated remediation
- `/remediate` Remediation Studio.
- Human explicitly APPROVES or REJECTS the exact proposal.
- Approval re-fetches and revalidates proposal/commit/file/hunk/before/after state.
- Writes occur only on isolated deterministic `incident-fix/...` branches.
- Only the exact approved sequence is replaced.
- Written content is re-read and verified.
- Frontend code runs dependency install + production build in a fresh clone.
- Backend Python runs compile + pytest in a fresh clone.
- Documentation-only changes use exact content-integrity validation.
- Unknown executable code types fail closed until a trusted validator exists.
- Draft PR is created only after validation passes.
- No automatic merge or production deployment exists.

### Retry-safe remediation and idempotency
- Exact incident + proposal receives a deterministic `REM-...` identity.
- Duplicate approvals are serialized in the current API process.
- Completed successful remediation is reconstructed from the audit timeline instead of rewritten.
- Deterministic branches replace timestamp-suffixed duplicates.
- Interrupted retries can reuse an exact branch when state remains safe.
- Already-patched exact branches are reused without rewriting.
- Conflicting branch state fails closed.
- Existing open PR is reused; matching closed PR blocks automatic recreation.
- Audit metadata records branch, commit, PR, validation and reuse state.

### Live GitHub CI verification
- Build workflow runs on `incident-fix/**` pushes and PRs targeting `main` or `develop`.
- `GET /api/v1/incidents/{incident_id}/patch-verification` reads actual PR/commit/check-runs/status.
- Derived state is `PASS`, `FAIL`, `PENDING` or `NO_CHECKS`; absence of checks is never success.
- Failure escalates; PASS remains `VERIFYING` until human review/runtime verification.
- Remediation Studio exposes live check details/links.

### Evaluation Lab
- Versioned deterministic benchmark `2026.09.11-v1` via `GET /api/v1/evaluation/run`.
- Measures routing, expected retrieval, RCA grounding, intentional no-match escalation, risk policy, unsafe-action blocking and approval-gate correctness.
- `/evaluation` exposes measured numerators/denominators and expected-vs-observed cases.
- Metrics are computed by backend functions when run; no accuracy value is hard-coded in the UI.
- Benchmark results are not presented as universal real-world accuracy.

### Reproducible startup and clean-clone acceptance
- Exact direct backend package versions.
- Exact direct frontend/tooling versions.
- Committed `frontend/package-lock.json` lockfile v3 with integrity hashes.
- Bootstrap requires lockfile and uses `npm ci`.
- `.python-version` = Python 3.11; `.nvmrc` = Node 22.23.2.
- `scripts/preflight.py`, `scripts/bootstrap.py`, `scripts/acceptance.py`.
- Windows: `verify.bat`, `start.bat`, `stop.bat`.
- Unix/macOS: `scripts/verify.sh`, `scripts/start.sh`, `scripts/stop.sh`.
- Launcher picks the first free backend port (preferred `8000`, fallback beginning `8011`) and frontend port (preferred `5173`, fallback beginning `5181`).
- Actual selected API base is injected into Vite using `VITE_API_BASE_URL`.
- Development CORS accepts local `localhost` / `127.0.0.1` origins on local ports; production does not use that broad development rule.
- Launcher waits for backend `/health` and frontend HTTP before reporting `READY`.
- Selected ports and launcher PIDs are stored under ignored `.run/` state.
- GitHub Actions performs a real `windows-latest` clean-checkout preflight/bootstrap/acceptance path.

### Readiness and evidence-security hardening
- `GET /api/v1/evaluation/readiness` and `/readiness` provide a judge/operator-facing readiness surface.
- Reports `READY`/`DEGRADED`, `LIVE_FIRST`/`FALLBACK_DEMO`, configuration checks and GitHub access mode without returning credential values.
- Readiness explicitly shows that repository writes require human approval, high-risk actions are recommendation-only, auto-merge is disabled and auto-production-deploy is disabled.
- Incident title, description, environment and logs redact recognized credential patterns before normal persistence/display.
- GitHub commit messages, issue titles/labels, diff lines and bounded source snippets redact recognized credential patterns before UI exposure.
- Repository content is explicitly treated as **untrusted evidence only**, never executable instructions.
- Prompt-like repository text is detected deterministically and surfaced as an untrusted-data warning.
- This detection/redaction is defense-in-depth, not a claim of complete prompt-injection or secret-scanning coverage.

### Verification and memory
- PASS / FAIL / INCONCLUSIVE runtime-verification endpoint/UI.
- PASS marks an incident resolved; failure/inconclusive escalates.
- Verified resolution stores symptoms, component, severity, working RCA, approved remediation and verification evidence for later retrieval.

### Emergency fallback
- Version-controlled deterministic fixtures exist for internet/provider failure.
- `DEMO_MODE` defaults to `false`.
- Fallback execution remains visibly `SIMULATED/DEMO` and is never presented as live success.

## Latest confirmed validation

GitHub Actions run **#335** / run ID `34594076848` on implementation head `1a9197cece79f5b3b1e59826ff99ae09f5b54864` completed successfully:

```text
Backend compile:                      PASS
Backend tests:                        59 passed, 2 dependency warnings, 0 failures
Frontend locked npm install:          PASS
Frontend TypeScript/Vite build:       PASS
Windows launcher syntax validation:   PASS
Windows strict environment preflight: PASS
Windows clean-checkout bootstrap:     PASS
Windows clean-clone acceptance:       PASS
```

The subsequent milestone-document commit changes documentation only and does not alter the tested executable code.

Current regression coverage includes triage, risk, persistence, retrieval, RCA, GitHub evidence, stale-write rejection, patch proposal/execution, idempotency/retry reuse, CI verification, Evaluation Lab, dynamic-port CORS/startup behavior, readiness secrecy/policy state, incident credential redaction, prompt-like untrusted-instruction detection, repository diff credential redaction and verified-memory behavior.

## Current live path

```text
Incident + repository
→ Persist + triage / route
→ Historical retrieval
→ Live GitHub evidence
→ Real commits + files + diff hunks
→ Bounded source context
→ Evidence-backed RCA
→ Exact patch proposal (NO WRITE)
→ Human APPROVE / REJECT
→ Stable remediation identity
→ Fresh proposal/file revalidation
→ Deterministic isolated fix branch
→ Exact patch OR safe retry reuse
→ Deterministic validation
→ Draft PR only if green OR reuse exact existing PR
→ Real GitHub CI verification
→ Human review / runtime verification
→ Resolved or escalated
→ Verified resolution memory
```

Parallel proof surfaces:

```text
Evaluation Lab → measured deterministic benchmark
System Readiness → runtime mode + configuration + safety boundary
```

Reproducible operator path:

```text
Fresh clone → preflight → locked bootstrap → automatic free ports
→ acceptance → one-command start → backend + frontend health → READY
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
11. ~~Live GitHub repository investigation.~~
12. ~~Real diff parsing + suspicious-hunk ranking + RCA grounding.~~
13. ~~Operator-grade Evidence Lab + bounded source context.~~
14. ~~Exact bounded patch proposal before repository write.~~
15. ~~Approval-gated isolated branch + exact patch + validation.~~
16. ~~Draft PR only after validation; never auto-merge.~~
17. ~~Real GitHub CI/check verification.~~
18. ~~Repeatable Evaluation Lab + measured scorecard.~~
19. ~~Remediation idempotency and retry-safe branch/PR reuse.~~
20. ~~Locked dependencies + preflight + dynamic-port one-command startup + Windows clean-clone acceptance.~~
21. ~~Judge-facing readiness + credential redaction + untrusted-evidence/prompt-injection hardening baseline.~~
22. Final submission freeze: clean-clone rehearsal, judge-flow rehearsal, docs/screenshots, integration review and release candidate.

## Next highest-value milestone

**Release-candidate rehearsal, not more random features.**

```text
fresh pull / verify
→ one-command start
→ readiness check
→ golden incident demo
→ Evidence Lab
→ patch proposal
→ explicit approval
→ validation / Draft PR
→ live CI check
→ Evaluation Lab
→ recovery/fallback rehearsal
→ README/screenshots/docs audit
→ release-candidate freeze
```

## Known implementation risks / truth boundaries

- Exact hackathon problem-statement constraints override generic assumptions if they differ from this direction.
- Commit/hunk correlation is heuristic investigation guidance, not causal proof.
- Current patch strategy is a conservative hunk-revert candidate, not guaranteed best semantic fix.
- Current benchmark is intentionally small/deterministic; a perfect score is not a general accuracy claim.
- GitHub rate limits/network availability can affect live evidence/check polling.
- GitHub can omit patch/content for binary or large files; missing evidence stays missing.
- In-process approval serialization fits the single-process MVP; horizontal scale needs a shared idempotency store/database constraint.
- Passing CI proves configured checks passed; it does not prove production recovery or justify merge.
- Python top-level requirements are pinned, but transitive Python dependencies are still resolved by pip rather than a fully hashed lock.
- Deterministic redaction and injection-marker detection are best-effort safeguards, not complete DLP/content-security systems.
- No automatic merge, production deployment, destructive database operation, unrestricted repository write, IAM mutation or secret mutation is permitted.
- Public repository history must never contain real tokens, credentials or private operational data.

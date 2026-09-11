# Implementation Progress

Last updated: 2026-09-11  
Active release-candidate branch: `agent-build-core`  
Draft integration PR: `#1` → `develop`  
Project name: **AI Agentic Bug Router**

## Status

**Planned hackathon MVP implementation scope: COMPLETE, real-use audited, and IIT Bombay demo-hardened.**

The project is in release-candidate hardening. Prefer regression fixes, evidence-quality improvements, rehearsal and documentation over broad new scope. `main` remains untouched until the team explicitly approves final submission promotion.

This completion statement is scoped to the agreed hackathon MVP; it is not a claim of universal bug-free or enterprise-production completeness.

Frozen release record: [`docs/RELEASE_CANDIDATE_FREEZE.md`](RELEASE_CANDIDATE_FREEZE.md).  
Real-use audit: [`docs/REAL_USE_AUDIT.md`](REAL_USE_AUDIT.md).  
IIT Bombay final demo guide: [`docs/IIT_BOMBAY_FINAL_DEMO.md`](IIT_BOMBAY_FINAL_DEMO.md).  
Real local repair proof: [`docs/REAL_AUTOFIX_PROTOTYPE.md`](REAL_AUTOFIX_PROTOTYPE.md).

## Exact-preview AutoFix write hardening — 2026-09-11

The real local-workspace `/prototype` flow now preserves the same approval principle used by GitHub remediation: **the operator-reviewed patch is the only write authority**.

- `POST /api/v1/autofix/{target_id}/proposal` remains a no-write preview and arms that exact `WorkspaceFixProposal` server-side.
- `POST /api/v1/autofix/{target_id}/apply` refuses direct execution when no reviewed proposal is armed.
- Apply consumes the exact reviewed proposal once instead of regenerating or substituting a new AI/deterministic candidate at write time.
- Reset invalidates the armed proposal before restoring the broken demo baseline.
- A fresh Scan invalidates any previously armed proposal before collecting new evidence.
- Every new Preview attempt invalidates the previous proposal before replanning, so a failed re-preview cannot leave older write authority armed.
- The `/prototype` UI enables Auto Fix only after a successful visible Preview and disables the write path again after execution.
- If Apply fails during fresh-state validation, the stale diff is removed from the UI and the operator must preview again.
- Failed Reset/Scan attempts no longer leave old scan evidence presented as current state.
- Current target/diagnosis/file state is rechecked before the write.
- The source must still exactly match the reviewed `before` state; a file change between Preview and Apply is rejected as stale.
- The reviewed edit is written only inside the allowlisted workspace and the same real validator is rerun.
- Failed validation restores the original source and does **not** silently auto-apply a substitute patch; a new operator preview is required.
- Regression coverage includes no-preview rejection, exact preview→apply equality, one-time consumption, reset invalidation, scan invalidation, failed-repreview invalidation, and stale-source mutation rejection.
- The Windows launcher now prints direct `Real AutoFix` (`/prototype`) and `AI Reasoning` (`/ai`) URLs after readiness, reducing demo-route ambiguity.
- For this single-process MVP, the armed proposal is held in process. A horizontally scaled production service should move approval state and one-time consumption to a shared transactional store.

This closes both the original trust-boundary gap (Apply regenerating a proposal after Preview) and the live-demo state gaps found during final rehearsal (Apply enabled before Preview, stale approvals surviving evidence refresh, and stale diffs remaining retryable after rejected execution).

## IIT Bombay judge/demo hardening — 2026-09-11

- Shared responsive navigation across Incident Command, Real AutoFix, Judge Demo, AI Reasoning Lab, Evidence Lab, Remediation, Evaluation Lab and Readiness.
- `/prototype` provides a real local broken-project proof: failing tests → grounded diagnosis → exact preview → reviewed file edit → same validator → PASS or rollback.
- `/ai` makes the agent architecture visible instead of presenting the product as a static dashboard.
- Judge-ready problem → evidence → RCA → solution walkthroughs cover Authentication, Database, Frontend, Infrastructure and an Unknown/no-match safe-stop case.
- Optional grounded LLM synthesis can use a local OpenAI-compatible endpoint; deterministic triage, evidence, risk, approval, writes and verification remain authoritative outside the model.
- `AnalysisBundle.agent_trace` truthfully exposes `LLM_RAG` vs `DETERMINISTIC_RAG`, provider/model, retrieval sources and fallback reason.
- Provider/network/model failure falls back visibly to deterministic evidence reasoning; fallback is never mislabeled as live LLM execution.
- Remote LLM endpoints require HTTPS; plain HTTP is accepted only for localhost/loopback.
- The local AutoFix planner prefers zero-cost local-model reasoning when configured, but model text never gains arbitrary shell authority.

## Completed live MVP

### Foundation + incident lifecycle
- FastAPI/Pydantic backend and React/Vite/TypeScript frontend.
- SQLite incident persistence, lifecycle state, timestamps and auditable timeline.
- Deterministic triage for Authentication, Database, Backend, Frontend, Infrastructure and Unclassified incidents.
- Deterministic LOW/MEDIUM/HIGH action-risk policy.
- Responsive light-theme-first UI with persistent Light/Dark switcher.

### Agent intelligence + RAG
- Deterministic RAG baseline retrieves curated runbooks plus previously verified resolution memory.
- Explicit no-strong-match behavior prevents forced historical answers.
- Live GitHub commit/diff/source context is a separate evidence source rather than being mislabeled as historical RAG.
- Optional grounded LLM synthesis operates downstream of retrieval and repository evidence.
- Repository/log/runbook text is treated as untrusted data at the model boundary.
- The model does not control confidence, risk, approval, GitHub writes, merge/deploy decisions or verification outcomes.
- `/ai` provides a judge-facing architecture and problem-to-solution reasoning surface.

### Evidence, routing + RCA
- Curated local runbook/knowledge retrieval baseline.
- Verified resolution memory participates in later retrieval.
- Evidence-backed RCA hypothesis, confidence, next diagnostic, remediation and verification plan.
- Human escalation when evidence is insufficient.
- Component-to-team ownership can be configured with `TRIAGE_OWNER_MAP`.
- Live CODEOWNERS metadata is an advisory routing/review hint for highly ranked changed files when present.

### Live GitHub investigation
- Read-only investigation for an allowlisted repository.
- Real repository metadata, recent commits, commit details, changed files and open issues.
- Real unified-diff patches where GitHub provides them.
- Suspicious-hunk ranking using incident/code token correlation plus stack-trace/file-path hints.
- Bounded source context at the exact commit SHA.
- `/evidence` Engineering Evidence Lab with real GitHub links and ownership hints.
- Correlation is explicitly guidance, not proof of causation.

### Exact bounded GitHub patch proposal
- `POST /api/v1/incidents/{incident_id}/patch-proposal` creates a reviewable candidate with **no repository write**.
- Candidate is revalidated against fresh live evidence.
- Conservative `REVERT_SUSPICIOUS_HUNK` strategy only when the exact target remains available and clears `PATCH_PROPOSAL_MIN_CORRELATION`.
- Stale, ambiguous, weakly related or missing source state fails closed.
- Proposal contains exact file/base/hunk/before/after/diff/rationale/confidence/warnings/verification commands.

### Human-controlled GitHub remediation
- `/remediate` Remediation Studio.
- Explicit APPROVE / REJECT for the exact proposal.
- Approval revalidates fresh live state before writing.
- Writes only to deterministic isolated `incident-fix/...` branches.
- Only the exact approved sequence is replaced and re-read for integrity.
- Frontend validation uses locked `npm ci` + production build.
- Backend Python validation runs compile + pytest.
- Unknown executable/config/operational file types fail closed without a trusted validator.
- Draft PR only after validation passes.
- No automatic merge or production deployment.

### Real local-workspace AutoFix proof
- `/prototype` / `/autofix` operates on registered allowlisted local project targets, not unrestricted OS paths.
- Included `demo_targets/broken_auth_api` is a genuinely broken FastAPI service with real pytest proof.
- Scanner inventories bounded source files, runs a platform-defined validator and diagnoses a source/test contract mismatch.
- Local reasoning can use Ollama/Qwen-class or compatible models when available; deterministic source/test evidence remains a safe fallback.
- Model-generated patch candidates are bounded to validated file/search/replace semantics; model text cannot run arbitrary shell commands.
- Every API write requires the exact previously previewed proposal.
- Scan, Reset and new Preview attempts invalidate older reviewed state before proceeding.
- Apply is one-shot and stale preview/source state fails closed.
- Verification reruns the same test command; failure rolls the file back.
- `/prototype` exposes actual BEFORE FAIL → AFTER PASS evidence, diff, provider/strategy and audit trail.

### Retry safety + idempotency
- Stable `REM-...` remediation identity for an exact incident/proposal.
- Duplicate approvals reuse completed remediation instead of writing again.
- Deterministic branch naming and safe partial-state recovery.
- Already-patched exact branches are reused without rewriting.
- Conflicting branch/PR state fails closed.
- Existing open exact PR is reused instead of duplicated.
- Timeline stores remediation identity, branch, commit, PR, validation and reuse state.

### Real GitHub CI + derived verification evidence
- CI workflow runs on remediation branches and relevant PRs.
- `GET /api/v1/incidents/{incident_id}/patch-verification` reads real PR/commit/check/status state.
- Derived CI result: `PASS`, `FAIL`, `PENDING` or `NO_CHECKS`.
- Canonical verification evidence is tied to the real repository, remediation commit, Draft PR and observed checks.
- Real CI failure derives incident verification `FAIL`, records the derivation and escalates.
- Pending/no-check state is inconclusive.
- Green CI is structured evidence only; it does **not** auto-resolve because configured checks do not prove the original runtime symptom recovered.
- Runtime/human verification remains required after CI PASS.

### Evaluation Lab
- Versioned deterministic benchmark `2026.09.11-v1` via `GET /api/v1/evaluation/run`.
- Measures routing, retrieval, RCA grounding, no-match escalation, risk policy, unsafe-action blocking and approval-gate behavior.
- `/evaluation` shows measured numerators/denominators and expected-vs-observed cases.
- No accuracy metric is hard-coded into the frontend.
- Benchmark score is explicitly not a universal real-world accuracy claim.

### Reproducible startup
- Exact direct backend/frontend package versions and committed npm lockfile v3.
- Bootstrap requires the lockfile and uses `npm ci`.
- `.python-version` = Python 3.11; `.nvmrc` = Node 22.23.2.
- Preflight, bootstrap and acceptance scripts.
- Windows `verify.bat`, `start.bat`, `stop.bat` and Unix/macOS equivalents.
- Launcher selects free local ports and injects the actual API URL into Vite.
- Backend/frontend health gates before `READY`.
- Startup output includes direct links for the real AutoFix and AI reasoning surfaces.
- GitHub Actions performs a real Windows clean-checkout bootstrap + acceptance path.

### Readiness + security hardening
- `GET /api/v1/evaluation/readiness` and `/readiness` surface READY/DEGRADED and LIVE_FIRST/FALLBACK_DEMO state.
- Readiness reports authentication/configuration state without returning credentials.
- Incident fields/logs redact recognized credential patterns before normal persistence/display.
- GitHub commit/issue/diff/source text redacts recognized credential patterns before UI exposure.
- Repository content is untrusted evidence only, not executable instructions.
- Prompt-like repository text is deterministically flagged as untrusted data.
- Local workspace access rejects traversal and excludes secret/system/build directories.
- These are defense-in-depth controls, not claims of complete DLP or universal prompt-injection prevention.

### Judge Mode
- `/demo` provides the controlled golden repository workflow.
- Repository write is locked by default.
- Live remediation requires separate arming plus explicit human approval.
- Missing/stale/ambiguous live evidence produces visible `SAFE_STOP` behavior.
- Exact proposal diff, file, confidence and candidate commit are reviewable before approval.
- `/prototype` complements Judge Mode with a directly inspectable real local application that is broken, repaired and retested on disk.

### Verification + resolution memory
- PASS / FAIL / INCONCLUSIVE runtime verification.
- PASS resolves; failed/inconclusive verification escalates.
- Verified resolution stores reusable symptoms/component/severity/RCA/remediation/evidence.

### Emergency fallback
- Deterministic fixtures exist only for internet/provider failure.
- Fixture catalog covers Authentication, Database, Frontend, Infrastructure and Unknown/no-match demonstrations.
- `DEMO_MODE` defaults `false`.
- Fallback remains visibly `SIMULATED/DEMO` and cannot be confused with live success.

## Real-use audit result

The audit identified and fixed weak stack-trace/file-path weighting, weakly correlated patch eligibility, unsafe/unknown validator gaps, unlocked frontend validation, hard-coded ownership, missing CODEOWNERS hints, and missing canonical CI verification evidence. Subsequent hardening added grounded model/fallback traces and exact-preview binding for local-workspace writes.

The suite now explicitly covers realistic multi-domain incidents, unknown/no-match behavior, path-to-code correlation, weak-patch rejection, unsupported-validator rejection, configurable routing, CODEOWNERS hints, CI failure/inconclusive derivation, deterministic/LLM fallback behavior, local-model patch bounds, workspace escape rejection, no-preview write rejection, exact reviewed-patch execution, reset invalidation, scan invalidation, failed-repreview invalidation and stale-preview rejection.

## Latest confirmed full release-candidate validation

GitHub Actions run **#561** / run ID `34606860119` on executable hardening head:

`84c8d72e235ffed0bf4d62386e531694855a2460`

completed successfully:

```text
Backend compile:                       PASS
Backend tests:                         90 passed, 2 dependency warnings, 0 failures
Frontend locked npm install:           PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax validation:    PASS
Windows strict environment preflight:  PASS
Windows clean-checkout bootstrap:      PASS
Clean-clone acceptance:                PASS
Overall workflow:                      PASS
```

The two backend warnings are dependency deprecations from FastAPI/Starlette test infrastructure; they are not test failures. This is the latest fully verified executable head for the final `/prototype` sequencing, approval invalidation and stale-error-state hardening described above.

## Completed product path

```text
Incident + repository
→ persist + deterministic triage / real-team route
→ RAG: runbooks + verified resolution memory
→ live GitHub evidence
→ commits + files + diff hunks + bounded source
→ evidence-backed RCA + next diagnostic
→ deterministic risk policy
→ exact no-write patch proposal
→ HUMAN APPROVE / REJECT
→ stable remediation identity + stale-state validation
→ isolated fix branch + exact approved patch
→ deterministic trusted validation
→ Draft PR only if green
→ real GitHub CI/check verification
→ derived verification evidence
→ runtime/human verification
→ resolved or escalated
→ verified resolution memory
```

Real local proof path:

```text
/prototype
→ real broken target
→ run real failing tests
→ source/test-grounded diagnosis
→ preview exact no-write patch
→ arm exact reviewed proposal
→ explicit Apply consumes that proposal once
→ stale preimage check
→ write exact reviewed change
→ rerun same tests
→ PASS = FIXED / FAIL = rollback
```

## P0 sequence

1. ~~Incident intake + triage/routing.~~
2. ~~Persistence + audit timeline.~~
3. ~~Historical retrieval.~~
4. ~~Evidence-backed RCA.~~
5. ~~Risk-gated remediation.~~
6. ~~Explicit human approval.~~
7. ~~Verification + resolution transition.~~
8. ~~Verified-resolution memory.~~
9. ~~Emergency deterministic fallback.~~
10. ~~Bounded GitHub issue action.~~
11. ~~Live GitHub repository investigation.~~
12. ~~Diff parsing + suspicious-hunk ranking.~~
13. ~~Evidence Lab + source context.~~
14. ~~Exact no-write patch proposal.~~
15. ~~Approval-gated isolated branch + patch + validation.~~
16. ~~Draft PR only after green validation.~~
17. ~~Real GitHub CI/check verification.~~
18. ~~Derived incident-verification evidence from remediation/CI state.~~
19. ~~Evaluation Lab + measured scorecard.~~
20. ~~Idempotent retry-safe remediation.~~
21. ~~Locked dependencies + preflight + dynamic-port startup + clean-clone acceptance.~~
22. ~~Readiness + redaction + untrusted-evidence hardening.~~
23. ~~Judge Mode + recovery/presentation flow.~~
24. ~~Release-candidate contract + automated freeze acceptance.~~
25. ~~Real-use usefulness audit and regression hardening.~~
26. ~~Shared navigation + IIT Bombay problem/solution demo flow.~~
27. ~~Optional grounded LLM synthesis + auditable deterministic fallback.~~
28. ~~LLM transport hardening + HTTPS/local-model adapter tests.~~
29. ~~Real local-workspace AutoFix with failure→edit→same-validator proof.~~
30. ~~Exact-preview binding, one-time apply, reset/scan/repreview invalidation and stale-source rejection for local AutoFix writes.~~

## What remains before final submission

No broad feature development is required for the hackathon MVP. Continue only with verified regression fixes, evidence-quality improvements and team-controlled finalization:

```text
pull latest agent-build-core
→ run verify.bat locally
→ run start.bat locally
→ open the printed Real AutoFix URL
→ rehearse /prototype from Reset → Scan → Preview → Auto Fix
→ open /readiness and confirm the reported mode
→ rehearse /ai with JWT regression, then one no-match case
→ rehearse /demo on the actual hackathon laptop/network
→ test one realistic incident through /evidence
→ optionally configure/test the chosen local LLM provider without exposing credentials
→ capture desired screenshots
→ proofread submission documentation
→ explicitly approve branch promotion
→ promote reviewed release to submission branch/main
```

Branch promotion is intentionally **not** performed automatically.

## Known truth boundaries / future work

- Exact official hackathon problem-statement constraints override generic assumptions if different.
- Commit/hunk correlation is heuristic guidance, not causal proof.
- Current GitHub patch strategy is conservative and is not guaranteed to be the best semantic fix.
- Local AutoFix currently demonstrates a bounded registered target and tested repair class; it is not a claim that arbitrary software defects can always be autonomously repaired.
- Benchmark is intentionally small/deterministic and is not universal accuracy.
- GitHub rate limits/network availability can affect live evidence/check polling.
- CI PASS proves configured checks passed, not production recovery.
- Python direct requirements are pinned; transitive Python dependencies are not yet fully hash-locked.
- In-process GitHub remediation serialization and the local AutoFix reviewed-proposal cache fit this single-process MVP. Horizontal scale should use shared transactional idempotency/approval state.
- CODEOWNERS handling supports common standard patterns but does not claim every exotic escaping edge case.
- Redaction/injection detection are best-effort defense-in-depth controls.
- No custom ML model is trained in this MVP. Intelligence comes from deterministic routing/RAG, verified incident memory, live repository evidence correlation, optional grounded LLM synthesis, bounded local patch planning, risk-aware orchestration and verification.
- A real external/local LLM call is only described as live when it is configured and successfully executed; the UI exposes fallback state instead of fabricating provider success.
- No automatic merge, production deployment, destructive data operation, unrestricted repository/OS write or IAM/secret mutation is permitted.
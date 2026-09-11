# KURUKSHETRA 2.0 — LIVE PROJECT STATUS

> Source of truth for handoff between teammates, ChatGPT, Codex, Astra and other coding sessions.

## Last Updated

2026-09-12

## Current Phase

**HACKATHON MVP COMPLETE — RELEASE-CANDIDATE HARDENING / REHEARSAL**

The AI Agentic Bug Router is implemented on `agent-build-core` and is being hardened for judging. Broad feature expansion is frozen. Current work is limited to regression fixes, evidence quality, safety, reproducibility, demo recovery and documentation accuracy.

`main` remains untouched. Draft PR #1 targets `develop` and remains intentionally unmerged until explicit team approval.

## Repository State

- Repository: `omghotekar01-dotcom/KURUKSHETRA-2.O`
- Stable/default branch: `main`
- Integration branch: `develop`
- Active release-candidate branch: `agent-build-core`
- Draft integration PR: `#1` → `develop`
- Repository visibility: PUBLIC
- Current `agent-build-core` head before this status correction: `e743e1c22b71525f87ce5fac555ddbe0c40fceb6`
- Latest completed push CI before this status correction: Build and test run **#791** / run ID `34644314306` — **SUCCESS**

## Current Product

The implemented product is a LIVE-FIRST, evidence-backed engineering incident-response and bounded remediation MVP.

Canonical flow:

```text
Incident / bug report
→ deterministic triage + owner routing
→ persistence + audit timeline
→ runbook / verified-resolution retrieval
→ live GitHub commits, files, issues, diffs and bounded source context
→ evidence-backed RCA + next diagnostic
→ deterministic risk policy
→ exact no-write patch proposal
→ explicit human APPROVE / REJECT
→ fresh stale-state validation
→ isolated incident-fix branch
→ apply only the exact approved replacement
→ deterministic validation
→ Draft PR only when validation is green
→ real GitHub Actions / commit-status evidence
→ derived incident-verification evidence
→ external human GitHub review / merge
→ runtime or human recovery verification
→ resolved or escalated
→ verified resolution memory
```

The system does **not** auto-merge, deploy production, execute arbitrary model-generated shell commands, perform destructive production actions or expose secrets.

## Implemented Judge-Facing Surfaces

- `/` / `/workspace` — AI Workspace for bug description, GitHub repository context, file attachment and investigation.
- `/test` — Test Lab workflow chooser.
- `/incidents` — Incident Command and incident lifecycle views.
- `/prototype` — controlled real AutoFix proof using allowlisted broken projects and the same validator before/after.
- `/intake` — isolated judge-supplied source/test intake with explicit trusted-test execution.
- `/ai` — AI Reasoning Lab showing triage, RAG, repository evidence, RCA synthesis, fallback mode and policy gate.
- `/demo` — controlled golden Judge Mode.
- `/evidence` — live read-only GitHub evidence, ranked commits/hunks and bounded patch preview.
- `/remediate` — explicit human approval, exact patch application, validation, Draft PR creation and CI evidence.
- `/evaluation` — repeatable measured benchmark; no hard-coded headline accuracy.
- `/readiness` — live Qwen/GitHub/runtime readiness and safety boundary.

## Real Repair Proofs

### Built-in AutoFix

`/prototype` uses real allowlisted local project files and validators:

```text
Reset broken target
→ Scan + reproduce
→ validator FAIL
→ grounded diagnosis
→ exact Preview
→ one-time Apply of exactly that reviewed proposal
→ stale preimage check
→ real file edit
→ same validator rerun
→ PASS = FIXED
→ FAIL = rollback
```

Current repeatable target classes include authentication parsing, cart arithmetic and pagination regressions.

### Judge-Supplied Intake

`/intake` accepts up to 12 bounded text/code files, max 256 KB each, in an isolated temporary workspace.

Default mode is `STATIC_ONLY`; uploaded code is not executed. Explicit **Trusted test execution** may run bounded Python `test_*.py` with pytest. `VERIFIED_FIXED` is claimed only for the same trusted failing test changing from FAIL before the reviewed patch to PASS after it. Static-only success is labeled `STATIC_CHECK_PASSED`, not functional recovery.

## Live AI / RAG

Default zero-cost reasoning path:

```text
Ollama localhost / qwen3:4b
→ optional configured Gemini free-tier fallback
→ deterministic fallback only where an explicit safe rule exists
```

The product exposes a real model probe; configuration alone is not presented as proof of inference. Generic judge intake fails closed if a live model cannot return a valid bounded candidate and no explicit deterministic safe rule exists.

RAG is intentionally bounded to curated engineering runbooks and verified resolution memory. Live GitHub evidence is kept as a separate evidence source. Retrieved text, issue text, logs, comments and repository content are treated as untrusted data, never as authorization or policy instructions.

## Evaluation Lab

`/evaluation` runs backend-computed benchmark cases and exposes expected vs observed behavior. Current dimensions include:

- routing accuracy;
- retrieval hit / explicit no-match behavior;
- RCA evidence grounding;
- risk-policy behavior;
- unsafe-action blocking;
- approval-gate behavior.

Any score shown by the UI is scoped to the displayed benchmark fixture set. It must not be generalized into universal production accuracy.

## Remediation / Verification Policy

Medium-risk repository writes remain allowlisted and human approval-gated. Approval is bound to one exact visible proposal.

Current retry/idempotency protections include:

- fresh proposal/state revalidation;
- deterministic remediation identity;
- serialized execution in the single-process MVP;
- duplicate approval reuse;
- deterministic branch naming;
- already-patched branch reuse;
- exact open Draft PR reuse;
- stale source rejection;
- conflicting branch/PR fail-closed behavior.

Real CI/check state is converted into auditable incident-verification evidence:

- real CI `FAIL` may derive failed verification and escalate;
- `PENDING` / no checks stay inconclusive;
- `PASS` is strong evidence for the remediation commit but does **not** auto-resolve the original runtime incident;
- runtime/human verification remains authoritative for final recovery.

## Reproducibility / Startup

Implemented release hardening includes:

- Python target via `.python-version`;
- Node target via `.nvmrc`;
- pinned direct backend dependencies;
- committed npm lockfile;
- frontend bootstrap with `npm ci`;
- Windows and Unix/macOS startup paths;
- health gates before READY;
- stale/reused Windows PID safety handling;
- Windows clean-checkout bootstrap test;
- clean-clone acceptance suite;
- release-contract regression checks.

## Latest Confirmed CI

Build and test run **#791** / run ID `34644314306` completed successfully for head:

```text
e743e1c22b71525f87ce5fac555ddbe0c40fceb6
```

Confirmed workflow jobs:

```text
backend             SUCCESS
frontend            SUCCESS
windows-clean-clone SUCCESS
```

That run includes backend compilation/tests, locked frontend installation/build, Windows launcher checks, stale/reused PID regression protection, strict preflight, bootstrap, clean-clone acceptance and the release contract.

Do not invent new test counts or benchmark percentages unless a current reproducible run provides them.

## Safety / Truth Boundaries

- `.env` is untracked; secrets must never be committed or rendered into ordinary evidence.
- Repository investigation is read-only until explicit approval.
- Repository writes are allowlisted, exact-proposal-bound and review-gated.
- Prompt/repository/log content is untrusted evidence and cannot redefine policy.
- Uploaded judge code does not run unless explicitly trusted.
- Stale or ambiguous state fails closed.
- Failed repair validation rolls back where applicable.
- No in-product protected-branch merge endpoint exists.
- No auto-deploy or production mutation exists.
- Commit/hunk correlation is investigation guidance, not causal proof.
- CI PASS is evidence, not proof of production recovery.
- Simulation/demo mode is fallback-only and must remain visibly labeled.

## Current Work Policy

Feature freeze is active. Priority order for any remaining work:

1. fix verified regressions first;
2. protect safety / no-auto-merge boundaries;
3. improve evidence quality and recovery behavior;
4. keep CI, lockfiles, startup and clean-clone acceptance green;
5. rehearse the judge paths on the actual hackathon laptop;
6. update screenshots/docs only from real product states;
7. avoid broad late-stage architecture changes.

## Final Laptop Rehearsal

```text
pull latest agent-build-core
→ verify.bat
→ setup-local-ai.bat
→ start.bat
→ confirm LIVE LOCAL QWEN only if the real probe succeeds
→ /test choose the judge-appropriate proof path
→ /prototype Reset → Scan FAIL → Preview → Apply → same validator PASS
→ /intake attach trusted source + failing test → RAG/Qwen → Preview → Apply → VERIFIED_FIXED
→ /ai run one known case + one safe-stop/no-match case
→ /evidence inspect real repository evidence
→ /remediate show exact proposal → approval → validation → Draft PR/CI boundary; do not merge
→ /evaluation show measured benchmark evidence
→ /readiness confirm integrations before judging
```

If an external integration fails, show the failure honestly and use the deterministic local proof path rather than fabricating success.

## Canonical Handoff Reading

Before substantial changes read, in order:

1. `TEAM_BRAIN/README.md`
2. `TEAM_BRAIN/A_TO_Z_INDEX.md`
3. this file
4. `TEAM_BRAIN/EVENT_AND_CONSTRAINTS.md`
5. `TEAM_BRAIN/CANONICAL_PROJECT_DESCRIPTION.md`
6. `TEAM_BRAIN/DECISION_LOG.md`
7. `TEAM_BRAIN/SECURITY_AND_GUARDRAILS.md`
8. `TEAM_BRAIN/EVALUATION_FRAMEWORK.md`
9. relevant implementation docs and current code
10. latest branch / PR / CI state

For detailed current implementation truth, use `docs/IMPLEMENTATION_PROGRESS.md` and `docs/PATCH_REMEDIATION_MILESTONE.md`.

## Known Future Work After Hackathon

- move in-process review/session/idempotency state to shared transactional storage for multi-worker deployment;
- replace explicit trusted uploaded-code execution with a hardened hostile-code sandbox if that scope is pursued;
- fully hash-lock transitive Python dependencies;
- expand CODEOWNERS pattern support;
- strengthen DLP/prompt-injection defenses beyond current defense-in-depth controls;
- add production-grade observability and external deployment controls only behind separate high-risk authorization systems.

Branch promotion remains manual. `main` remains untouched.

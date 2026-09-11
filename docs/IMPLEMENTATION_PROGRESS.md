# Implementation Progress

Last updated: 2026-09-11  
Active release-candidate branch: `agent-build-core`  
Draft integration PR: `#1` → `develop`  
Project name: **AI Agentic Bug Router**

## Status

**Hackathon MVP scope is complete and in release-candidate hardening.**

The product now has both a controlled real repair proof and a judge-supplied challenge path. Continue with regression fixes, rehearsal and evidence-quality improvements only; do not add broad scope before the final. `main` remains untouched until explicit team approval.

This status is scoped to the implemented MVP. It is not a claim that arbitrary software defects can always be autonomously repaired or that a green CI run proves production recovery.

Key docs:

- [`docs/IIT_BOMBAY_FINAL_DEMO.md`](IIT_BOMBAY_FINAL_DEMO.md)
- [`docs/JUDGE_SUPPLIED_INTAKE.md`](JUDGE_SUPPLIED_INTAKE.md)
- [`docs/REAL_AUTOFIX_PROTOTYPE.md`](REAL_AUTOFIX_PROTOTYPE.md)
- [`docs/REAL_USE_AUDIT.md`](REAL_USE_AUDIT.md)
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](RELEASE_CANDIDATE_FREEZE.md)

## Current judge-facing proof surfaces

### `/prototype` — guaranteed real repair proof

Registered allowlisted projects are genuinely broken on disk and are validated with their own pytest contracts.

Current repeatable target classes include:

- Bearer-authentication parser regression;
- cart-total arithmetic regression;
- pagination offset regression.

Flow:

```text
Reset real broken target
→ Scan + reproduce
→ real pytest FAIL
→ source/test-grounded diagnosis
→ optional Qwen candidate OR truthful deterministic safe fallback
→ exact no-write Preview
→ operator reviews exact diff
→ one-time Apply of exactly that reviewed proposal
→ stale preimage check
→ real file edit
→ same pytest rerun
→ PASS = FIXED
→ FAIL = original source restored
```

Approval hardening is complete:

- Apply is unavailable until a visible Preview exists.
- Scan, Reset and every new Preview invalidate older write authority.
- Apply consumes a reviewed proposal once.
- A failed re-preview cannot leave an older proposal armed.
- Source mutation after Preview fails closed.
- A failed Apply removes stale UI state and requires a fresh Preview.
- Failed validation restores the exact original file and never substitutes an unreviewed patch.

### `/intake` — judge-supplied bug + files

A judge/operator can now type a bug report and attach their own bounded source/test files. The system creates an ephemeral isolated copy instead of granting the model arbitrary laptop access.

Supported intake contract:

- up to 12 files;
- 256 KB maximum per file;
- allowlisted text/code types: Python, JS/JSX, TS/TSX, JSON, YAML, TOML, Markdown and text;
- traversal, absolute paths, Windows drive paths and secret/build directories rejected;
- sessions expire and live under a temporary intake root;
- model receives bounded uploaded text only;
- all edits remain inside the isolated session copy.

Flow:

```text
judge bug report + attached files
→ isolated temporary workspace
→ baseline validation
→ RAG over engineering runbooks
→ live grounded Qwen/Gemini candidate when connected
→ exact file/search/replace validation
→ visible no-write Preview
→ one-time operator review/approval
→ exact isolated edit
→ trusted pytest OR static verification
→ VERIFIED_FIXED / STATIC_CHECK_PASSED / ROLLED_BACK
```

#### Trusted test execution

Uploaded code is **not executed by default**.

Default `STATIC_ONLY` mode:

- compiles Python syntax;
- parses JSON;
- executes no uploaded code;
- may return `STATIC_CHECK_PASSED`;
- never claims functional recovery.

If the operator explicitly enables **Trusted test execution** and supplies Python `test_*.py`, the isolated session runs a bounded pytest command with reduced environment exposure and isolated bytecode cache.

`VERIFIED_FIXED` is permitted only when:

```text
same trusted test baseline BEFORE = FAIL
→ exact reviewed patch
→ same trusted test AFTER = PASS
```

Failed post-patch validation restores the original uploaded file and returns `ROLLED_BACK`.

## Live local AI / Qwen proof

Default zero-cost model path:

```text
Ollama localhost
→ qwen3:4b
→ optional configured Gemini free-tier fallback
→ deterministic fallback only where an explicit safe rule exists
```

`setup-local-ai.bat` now:

- verifies Ollama exists;
- starts/reaches the Ollama service;
- pulls `qwen3:4b`;
- confirms the model is installed;
- fails instead of falsely reporting readiness.

`POST /api/v1/autofix/model-runtime/probe` performs a **real chat-completions inference request** and reports provider, model, latency, reply and connection status.

`/intake` exposes this as **Test Qwen now**. Configuration alone is not presented as proof that a model call occurred.

Qwen-specific structured-output handling tolerates its optional reasoning `<think>` transport text while still validating only the final JSON object. Generic patch output remains constrained to one exact `file_path/search/replace/explanation` object over files actually supplied to the model.

Generic judge intake deliberately fails closed when no live model can produce a valid bounded candidate; it does not invent an arbitrary deterministic repair.

## RAG + reasoning

RAG is real but intentionally bounded:

- curated engineering runbooks;
- previously verified resolution memory for incident analysis;
- explicit no-strong-match behavior;
- judge intake retrieval over bug text + attached file evidence;
- live GitHub evidence remains a separate evidence source rather than being mislabeled as historical RAG.

Optional model synthesis runs downstream of deterministic evidence collection. Repository/uploaded/runbook text is treated as untrusted data, not system instructions.

The model does **not** control:

- confidence authority;
- risk classification;
- approval;
- unrestricted paths or shell commands;
- whether tests passed;
- GitHub merge/deploy;
- runtime verification outcome.

**The model can reason and propose; evidence and validators hold authority.**

## Incident + GitHub workflow

Implemented live path:

```text
Incident + logs + repository
→ persistence + deterministic triage / configurable team route
→ RAG: runbooks + verified resolution memory
→ live GitHub commits/issues/diffs/source
→ suspicious-hunk + stack/file correlation
→ CODEOWNERS advisory hints
→ evidence-backed RCA + next diagnostic
→ deterministic risk policy
→ exact no-write patch proposal
→ HUMAN APPROVE / REJECT
→ fresh stale-state validation
→ stable remediation identity
→ isolated incident-fix branch
→ exact approved replacement
→ trusted validation
→ Draft PR only if validation is green
→ real GitHub CI/check evidence
→ derived incident-verification evidence
→ runtime/human verification
→ resolved or escalated
→ verified resolution memory
```

Retry/idempotency hardening includes deterministic remediation identity, duplicate approval reuse, exact-branch reuse, conflict safe-stop and existing exact PR reuse.

CI behavior remains deliberately conservative:

- real CI failure can derive incident verification `FAIL` and escalate;
- pending/no checks remain inconclusive;
- CI PASS is structured evidence only and does **not** auto-resolve the original runtime incident.

## Evaluation Lab

`/evaluation` runs the deterministic benchmark rather than showing hard-coded accuracy claims. It measures routing, retrieval/no-match behavior, RCA grounding, risk policy, unsafe-action blocking and approval-gate behavior with visible numerator/denominator evidence.

Benchmark results are scoped to the displayed cases and are not universal real-world accuracy claims.

## Reproducible startup

- Python 3.11 target via `.python-version`.
- Node target via `.nvmrc`.
- pinned direct backend/frontend dependencies.
- committed npm lockfile v3.
- bootstrap requires `npm ci`.
- Windows project-owned Node/Vite lock recovery handles common Rolldown `EPERM` failures.
- `verify.bat` fails closed immediately when bootstrap fails.
- launchers select safe local ports and inject the actual backend URL into Vite.
- backend/frontend health gates must pass before `READY`.
- stale/missing/reused Windows launcher PID files are treated as hints rather than proof of process ownership; cleanup verifies the process before termination, will not kill the active launcher/ancestor tree, and remains non-fatal for stale cleanup races.
- CI now contains an explicit Windows regression test for both a nonexistent stale PID and a PID reused by the current PowerShell launcher process tree.
- Windows `start.bat` prints detected AI runtime plus direct URLs for `/prototype`, `/intake`, `/ai`, `/demo`, `/evidence`, `/remediate`, `/evaluation`, `/readiness`.
- Unix/macOS launcher exposes the same judge-facing routes.

## Release contract

`scripts/release_contract.py` protects the core feature set from accidental deletion. Acceptance requires, among other artifacts:

- Real AutoFix route/page;
- Judge Intake route/page/CSS;
- file attachment UI;
- explicit Trusted test execution control;
- live Qwen probe UI and backend endpoint;
- RAG display;
- preview-before-apply UI;
- isolated intake backend;
- intake/model-probe regression tests;
- judge-intake documentation;
- Windows and Unix launcher links.

## Security / truth boundaries

- `.env` is not tracked.
- recognized credentials are redacted from normal incident/repository evidence surfaces.
- investigation is read-only until explicit approval.
- every write is bound to one exact reviewed proposal.
- stale state fails closed.
- path traversal and sensitive/build directories are blocked.
- arbitrary judge-uploaded code is not executed unless explicitly trusted.
- failed repair validation rolls back.
- no automatic merge or production deployment exists.
- no arbitrary model-generated shell execution exists.
- no unrestricted OS/repository writes exist.
- commit/hunk correlation is investigation guidance, not causal proof.
- `STATIC_CHECK_PASSED` is not described as functional recovery.
- live AI is only claimed when a real model call/provenance supports it.

## Latest confirmed full executable validation

GitHub Actions run **#644** / run ID `34620804814` on release-candidate head:

`723a31b74ba044e7619545b1ab6ace08ae9b6ec7`

completed successfully on 2026-09-11:

```text
Backend compile:                       PASS
Backend tests:                         102 passed, 2 dependency warnings, 0 failures
Frontend locked npm install:           PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax validation:    PASS
Windows stale/reused PID safety test:  PASS
Windows strict environment preflight:  PASS
Windows clean-checkout bootstrap:      PASS
Windows clean-clone acceptance:        PASS
Release-candidate contract:            PASS
Overall workflow:                      PASS
```

The two Python warnings are dependency deprecations from FastAPI/Starlette test infrastructure and are not test failures.

This run closes the Windows startup regression observed during final laptop rehearsal: stale or PID-reused `.run` records no longer abort dependency bootstrap or cause the launcher to attempt to terminate its own process tree.

## P0 milestone closure

Completed milestones now include:

1. incident intake + triage/routing;
2. persistence + audit timeline;
3. RAG + verified resolution memory;
4. live GitHub evidence and RCA;
5. risk-gated remediation and explicit approval;
6. exact bounded patch proposal;
7. isolated patch branch + trusted validation + Draft PR;
8. real CI/check verification evidence;
9. retry-safe/idempotent remediation;
10. Evaluation Lab;
11. reproducible startup + clean-clone acceptance;
12. security/redaction/untrusted-evidence hardening;
13. Judge Mode;
14. grounded local/free LLM adapter and truthful fallback;
15. real local AutoFix failure→edit→same-validator proof;
16. exact Preview→Apply one-time binding;
17. multiple repeatable built-in regression targets;
18. live Qwen connectivity probe;
19. isolated judge-supplied bug/file intake;
20. explicit trusted-test execution boundary;
21. RAG + Qwen bounded repair over judge-supplied evidence;
22. release contract coverage for the judge-intake feature set;
23. Windows launcher stale/reused PID cleanup regression protection.

## Final laptop rehearsal

On the actual Windows hackathon laptop:

```text
pull latest agent-build-core
→ verify.bat
→ setup-local-ai.bat
→ start.bat
→ confirm startup says LIVE LOCAL QWEN when Ollama is intended
→ /intake: Test Qwen now and require live model-call success
→ /prototype: Reset → Scan FAIL → Preview → Apply → same pytest PASS
→ /intake: attach a small trusted source + failing test → RAG → Qwen diff → Apply → VERIFIED_FIXED
→ /ai: one known case + one no-match safe-stop
→ /evidence: one real repository evidence walkthrough
→ /remediate: show exact approval/Draft-PR boundary without merging
→ /evaluation: show measured benchmark evidence
→ capture screenshots / rehearse recovery path
```

If a judge supplies files you do not trust, leave Trusted test execution off. If model/network evidence is unavailable, show the failure honestly and use the guaranteed `/prototype` proof rather than fabricating AI success.

Branch promotion remains intentionally manual.

## Known future work

- A production multi-worker service should move in-process review/session/idempotency state to a shared transactional store.
- Judge intake currently focuses on bounded text/code evidence rather than arbitrary binary archives or full dependency sandboxing.
- Python trusted-test execution is an explicit hackathon-laptop trust mode, not a hardened hostile-code sandbox.
- Python direct requirements are pinned; transitive Python dependencies are not fully hash-locked.
- CODEOWNERS handling covers common patterns, not every exotic edge case.
- Redaction/prompt-injection defenses are defense-in-depth, not universal DLP guarantees.
- No custom ML model is trained in this MVP; intelligence combines deterministic routing/RAG, verified incident memory, live repository evidence, grounded local/free LLM reasoning, bounded orchestration and real validation.

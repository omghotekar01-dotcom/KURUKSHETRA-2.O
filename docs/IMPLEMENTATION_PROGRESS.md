# Implementation Progress

Last updated: 2026-09-12  
Active release-candidate branch: `agent-build-core`  
Draft integration PR: `#1` → `develop`  
Project name: **AI Agentic Bug Router**

## Status

**Hackathon MVP scope is complete and in release-candidate hardening.**

The product now has both a controlled real repair proof and a judge-supplied challenge path. Continue with regression fixes, rehearsal and evidence-quality improvements only; do not add broad scope before the final. `main` remains untouched until explicit team approval.

This status is scoped to the implemented MVP. It is not a claim that arbitrary software defects can always be autonomously repaired or that a green CI run proves production recovery.

### Latest safety correction

During the judge-UI polish pass, an in-product human-confirmed PR merge executor was briefly introduced. That conflicted with the canonical TEAM_BRAIN guardrail that treats protected-branch merge/deploy as high-risk and recommendation-only for this prototype. The executor, merge API/schema/service/tests and merge-specific UI were removed before release validation.

The enforced boundary is again:

```text
reviewed exact patch
→ isolated fix branch
→ deterministic validation
→ Draft PR
→ real GitHub CI/check evidence
→ external human repository review/merge
→ runtime/human verification
```

CI PASS is evidence for the remediation commit; it is not merge authority and does not auto-resolve the original incident. Remediation Studio retains the white/purple UI pass, compact layout, friendly failure messages and truthful shimmers for repository inspection, proposal generation, validation and CI reads.

### Latest CI verification hardening

A release-candidate review found two fail-closed gaps in the real GitHub verification path and fixed them before promotion:

1. a green combined GitHub commit status could previously mask an observed check-run that was marked `completed` but had no terminal conclusion, or a check-run with an unknown/unrecognized state;
2. CI was read for the recorded remediation commit, but the live Draft PR response was not explicitly required to still point at that exact commit.

The verifier now requires every observed check-run to be in a recognized terminal state with a recognized terminal conclusion before reporting `PASS`. Missing conclusions, unknown states and unfamiliar conclusions remain `PENDING` rather than inheriting a green aggregate state.

The live Draft PR is also bound back to the stored remediation execution: its current head SHA must exactly match the recorded remediation commit before any CI evidence is trusted. If the PR head changed after execution, verification fails closed and the operator must refresh remediation state instead of trusting checks from an older commit.

These checks strengthen evidence integrity only. They do not change the existing authority boundary: CI `PASS` remains structured evidence and runtime/human confirmation is still required to resolve the original incident.

### Latest adversarial-evidence hardening

A security regression review expanded the deterministic untrusted-evidence boundary without changing model or repository authority.

Recognized credential redaction now covers unquoted credential assignments in addition to the existing token families, Bearer values and quoted assignments. Key names can remain visible for debugging/auditability, while recognized values are replaced with `[REDACTED]` before normal evidence surfaces.

Prompt-injection detection now covers both the existing exact marker phrases and broader instruction-shaped evidence categories, including:

- instruction/safety override attempts;
- requests to fabricate test or validation success;
- requests to merge/approve repository changes;
- requests to reveal environment/secrets/credentials;
- requests to bypass approval, review, validation or guardrails.

The detector remains an audit signal only. Repository text, logs, diffs, issues and source snippets stay untrusted data; matching text never becomes an instruction or repository-write authority.

CI caught one output-contract regression in the first redaction implementation: an already-redacted quoted assignment was being normalized into an unquoted redaction shape. The matcher was corrected to exclude quote-prefixed values before promotion, preserving the established quoted-redaction contract while retaining the new unquoted coverage.

### Latest live-read retry hardening

The real GitHub CI-verification path now tolerates short-lived read failures without weakening any write or approval gate. Verification GETs retry a maximum of three times for transport errors and GitHub `502`/`503`/`504` responses only. Authentication, authorization, rate-limit and other non-transient HTTP failures still fail immediately.

This retry policy is intentionally limited to idempotent read-only verification requests. It never retries repository writes, approval decisions, branch creation, patch application, PR creation, merge or deployment. Regression coverage proves both a transient `ConnectError → 503 → success` recovery and immediate no-retry behavior for `401` authentication failure.

### Latest Evaluation Lab validation hardening

The repeatable Evaluation Lab now measures the previously missing **validation-success** dimension instead of stopping at routing/retrieval/RCA/policy metrics.

Benchmark version `2026.09.12-v2` adds a controlled trusted Python contract that runs in an isolated temporary directory. The evaluator writes the known broken authentication fixture and its trusted `test_app.py`, runs `python -m pytest -q`, requires a failing baseline, replaces only the controlled fixture source with the bounded repaired state, and reruns the **same** pytest contract. The case passes only on a real `FAIL → PASS` transition.

This metric is computed at request time and is not a hard-coded score. Validator exit codes and bounded output are exposed in the benchmark case evidence. The temporary fixture cannot write to the repository, create branches/PRs or execute model-generated shell commands.

The scorecard now contains 8 measured metrics and 21 benchmark cases, including `validation_success_rate`. Evaluation regression tests reuse one measured report per test module to avoid unnecessary repeated child-validator processes during CI, while the live `/api/v1/evaluation/run` endpoint still re-runs the benchmark on each request.

Key docs:

- [`docs/IIT_BOMBAY_FINAL_DEMO.md`](IIT_BOMBAY_FINAL_DEMO.md)
- [`docs/JUDGE_SUPPLIED_INTAKE.md`](JUDGE_SUPPLIED_INTAKE.md)
- [`docs/REAL_AUTOFIX_PROTOTYPE.md`](REAL_AUTOFIX_PROTOTYPE.md)
- [`docs/REAL_USE_AUDIT.md`](REAL_USE_AUDIT.md)
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](RELEASE_CANDIDATE_FREEZE.md)
- [`docs/EVALUATION_LAB.md`](EVALUATION_LAB.md)

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
- performs a real native `/api/chat` warm-up;
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
→ live Draft-PR head binding to recorded remediation commit
→ real GitHub CI/check evidence
→ derived incident-verification evidence
→ external human repository review/merge
→ runtime/human verification
→ resolved or escalated
→ verified resolution memory
```

Retry/idempotency hardening includes deterministic remediation identity, duplicate approval reuse, exact-branch reuse, conflict safe-stop, existing exact PR reuse, and bounded retry of transient **read-only** GitHub verification failures. Repository writes are never retried by the verification reader.

CI behavior remains deliberately conservative:

- real CI failure can derive incident verification `FAIL` and escalate;
- pending/no checks remain inconclusive;
- every observed check-run must be completed with a recognized terminal conclusion before CI can report `PASS`;
- the live Draft PR head must still equal the recorded remediation commit before its CI evidence is trusted;
- missing/unknown check conclusions and changed PR heads fail closed instead of inheriting a green aggregate state;
- CI PASS is structured evidence only and does **not** auto-resolve the original runtime incident;
- no in-product merge endpoint exists.

## Evaluation Lab

`/evaluation` runs benchmark version `2026.09.12-v2` rather than showing hard-coded accuracy claims. It measures routing, retrieval/no-match behavior, RCA grounding, risk policy, unsafe-action blocking, approval-gate behavior and a real controlled validation-success contract with visible numerator/denominator evidence.

The validation case uses an isolated temporary fixture and reports success only if the same trusted pytest contract fails before the controlled repair and passes afterward. Benchmark results are scoped to the displayed cases and are not universal real-world accuracy claims.

## Judge UI / Test Lab

The current UI pass keeps the project light-first with a white + purple system, Apple-like system typography, stronger card separation, denser layouts and bounded liquid-glass use on navigation/control surfaces. Code, diffs and terminal evidence remain on solid high-contrast surfaces.

- `/` / `/workspace`: compact engineering composer with visible drag/drop evidence attachment.
- `/test`: one entry point for repository incidents, uploaded files/tests, controlled broken projects/compilations and the governed Draft-PR path.
- left navigation collapses on desktop and persists the state locally.
- Judge Demo and Incident Command use denser layouts to avoid large empty vertical gaps.
- Evaluation/Remediation and long-running operations expose truthful shimmer/loading states instead of fabricated placeholder data.
- simulation/demo behavior remains fallback-only and visibly labeled.

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
- CI contains an explicit Windows regression test for both a nonexistent stale PID and a PID reused by the current PowerShell launcher process tree.
- Windows `start.bat` prints detected AI runtime plus direct URLs for `/test`, `/prototype`, `/intake`, `/ai`, `/demo`, `/evidence`, `/remediate`, `/evaluation`, `/readiness`.
- Unix/macOS launcher exposes the same judge-facing routes.

## Release contract

`scripts/release_contract.py` protects the core feature set from accidental deletion. Acceptance requires, among other artifacts:

- AI Workspace and Test Lab routes;
- collapsible persistent navigation;
- white/purple product styling and async shimmer layer;
- Real AutoFix route/page;
- Judge Intake route/page/CSS;
- file attachment UI;
- explicit Trusted test execution control;
- live Qwen probe UI and backend endpoint;
- RAG display;
- preview-before-apply UI;
- isolated intake backend;
- intake/model-probe regression tests;
- explicit no-auto-merge README boundary;
- Windows and Unix launcher links.

## Security / truth boundaries

- `.env` is not tracked.
- recognized credentials, including quoted and unquoted credential assignments, are redacted from normal incident/repository evidence surfaces.
- prompt-like repository evidence is audit-signaled but remains untrusted data and never gains instruction authority.
- investigation is read-only until explicit approval.
- every repository patch write is bound to one exact reviewed proposal.
- stale state fails closed.
- CI verification is bound to the current live Draft-PR head and the recorded remediation commit.
- ambiguous or incomplete GitHub check results cannot be upgraded to PASS by a green aggregate status.
- transient read-only GitHub verification failures use bounded retries; repository writes do not inherit this retry behavior.
- path traversal and sensitive/build directories are blocked.
- arbitrary judge-uploaded code is not executed unless explicitly trusted.
- failed repair validation rolls back.
- no automatic merge, in-product merge endpoint or production deployment exists.
- no arbitrary model-generated shell execution exists.
- no unrestricted OS/repository writes exist.
- commit/hunk correlation is investigation guidance, not causal proof.
- `STATIC_CHECK_PASSED` is not described as functional recovery.
- live AI is only claimed when a real model call/provenance supports it.

## Latest confirmed full executable validation

GitHub Actions **Build and test #831** / run ID `34664079242` on executable release-candidate head:

`e9a80e808ea4810f0588831df584f90c13ccceec`

completed successfully on 2026-09-12 UTC / IST:

```text
Backend compile:                       PASS
Backend tests:                         121 passed, 2 dependency warnings, 0 failures
Frontend locked npm install:           PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax validation:    PASS
Windows stale/reused PID safety test:  PASS
Windows strict environment preflight:  PASS
Windows clean-checkout bootstrap:      PASS
Windows clean-clone acceptance:        PASS
Overall workflow:                      PASS
```

The two Python warnings are dependency deprecations from FastAPI/Starlette test infrastructure and are not test failures.

This validation includes the Draft-PR-only remediation boundary, fail-closed ambiguous CI/check handling, live Draft-PR head binding to the recorded remediation commit, bounded retries for transient read-only GitHub verification failures, expanded untrusted-evidence injection signals, quoted/unquoted credential redaction regression coverage, the Test Lab and white/purple UI system, Qwen Windows warm-up checks, locked frontend dependencies, the clean-clone Windows acceptance path, and the measured Evaluation Lab validation-success contract.

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
23. Windows launcher stale/reused PID cleanup regression protection;
24. compact white/purple judge UI + collapsible navigation + Test Lab;
25. restored Draft-PR-only merge boundary after safety regression review;
26. fail-closed GitHub check-state handling + live Draft-PR head/commit verification binding;
27. broader adversarial-evidence detection + unquoted credential redaction with CI-backed regression coverage;
28. bounded transient retry handling for read-only GitHub verification with explicit no-write retry coverage;
29. measured Evaluation Lab validation-success metric using a real isolated same-pytest FAIL → PASS contract.

## Final laptop rehearsal

On the actual Windows hackathon laptop:

```text
pull latest agent-build-core
→ verify.bat
→ setup-local-ai.bat
→ start.bat
→ confirm startup says LIVE LOCAL QWEN when Ollama is intended
→ /test: choose the proof path appropriate to the judge input
→ /intake: Test Qwen now and require live model-call success
→ /prototype: Reset → Scan FAIL → Preview → Apply → same pytest PASS
→ /intake: attach a small trusted source + failing test → RAG → Qwen diff → Apply → VERIFIED_FIXED
→ /ai: one known case + one no-match safe-stop
→ /evidence: one real repository evidence walkthrough
→ /remediate: show exact approval/Draft-PR/CI boundary without merging
→ /evaluation: show measured benchmark evidence including Validation success
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
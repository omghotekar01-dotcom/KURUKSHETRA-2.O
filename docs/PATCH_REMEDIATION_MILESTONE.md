# Patch Remediation Milestone

Date: 2026-09-12
Branch: `agent-build-core`

## Status

**COMPLETE for the hackathon MVP.**

This document originally captured the first approval-gated GitHub remediation implementation. The follow-on work that was previously listed as the next milestone — real CI/check-derived verification evidence and the Evaluation Lab — is now implemented and covered by the current release-candidate flow.

## What is real

The live MVP can move from repository evidence to an approval-gated code remediation workflow:

```text
Incident
→ live GitHub evidence
→ ranked diff hunk + bounded source context
→ exact patch proposal (NO WRITE)
→ human APPROVE / REJECT
→ live proposal revalidation
→ stable remediation identity
→ isolated `incident-fix/...` GitHub branch
→ apply only the exact approved before/after replacement
→ re-read branch content to verify patch integrity
→ deterministic validation for supported code types
→ create/reuse a DRAFT pull request only when validation passes
→ inspect real GitHub Actions / commit-status evidence
→ derive auditable incident-verification evidence
→ runtime/human verification remains authoritative for final recovery
```

## Safety boundaries

- No repository write occurs during investigation or patch-proposal generation.
- Rejection creates no branch, commit or PR.
- Approval is tied to the exact proposal reviewed by the human.
- Before writing, fresh GitHub state is revalidated; stale, ambiguous or conflicting source state fails closed.
- Every approved change is isolated on a deterministic `incident-fix/...` branch.
- Only the exact approved sequence is replaced.
- The written branch file is re-read and checked for exact integrity before validation.
- Duplicate approvals reuse exact successful remediation state rather than writing twice.
- Existing exact branches and open exact Draft PRs are reused instead of duplicated.
- Conflicting retry/branch/PR state fails closed.
- A Draft PR is created only after configured validation passes.
- No automatic merge, production deployment, destructive action, unrestricted repository write or secret mutation exists.

## Validation behavior

Supported frontend changes use a locked dependency install plus production TypeScript/Vite build in a fresh clone of the isolated branch.

Supported backend/Python changes run compile and pytest in a fresh clone using the trusted project validation environment. Clean project bootstrap and CI now install the backend through pinned direct requirements plus `backend/constraints.txt`, which locks the resolved transitive dependency set validated by the release workflow.

Documentation-only changes use exact branch-content integrity validation when no executable validator is relevant.

Unknown executable/configuration types fail closed until a trusted deterministic validator is configured.

## Live authentication

Repository writes require configured GitHub credentials through the existing approved credential adapter. Missing credentials return `AUTH_REQUIRED`; they never fall back to simulated write success.

Secrets are not exposed through normal evidence or readiness surfaces, and `.env` remains untracked.

## Operator UI

`/remediate` exposes the Remediation Studio with:

- incident selection;
- live repository inspection;
- safest eligible patch candidate;
- exact current/replacement lines;
- unified diff preview;
- proposal confidence and verification plan;
- reviewer and note;
- explicit Reject and Approve actions;
- long-running validation state;
- isolated branch link;
- real validation results;
- Draft PR link when the gate passes;
- real CI/check verification state;
- auditable remediation/verification timeline evidence.

## Automatic CI/check-derived verification

The remediation loop reads real GitHub Actions/check/status state for the remediation commit/PR and converts it into canonical verification evidence.

Current policy is intentionally conservative:

- `FAIL` from real CI/check evidence can derive failed incident verification and escalate the incident;
- `PENDING` or no checks remain inconclusive;
- `PASS` is recorded as strong structured evidence but does **not** automatically resolve the original runtime incident;
- runtime/human verification is still required before declaring production recovery.

Every observed check-run must reach a recognized terminal state/conclusion, and the live Draft PR head must still match the recorded remediation commit before CI evidence is trusted. Check-runs are collected across all GitHub API pages before state derivation; incomplete or inconsistent pagination fails closed rather than trusting partial evidence. Transient **read-only** GitHub verification reads retry up to three times for transport failures and `502`/`503`/`504` responses; authentication/authorization and other non-transient failures fail immediately. This retry helper never retries repository writes.

This follows decision D-012: CI proves configured checks on the remediation commit, not necessarily that the original production symptom recovered.

## Retry / idempotency hardening

The current path includes:

- stable remediation identity for an exact incident/proposal;
- serialization around remediation execution in this single-process MVP;
- duplicate approval reuse;
- deterministic branch naming;
- safe partial-state recovery;
- already-patched exact-branch reuse;
- exact open-PR reuse;
- stale-source rejection;
- conflicting branch/PR safe-stop behavior;
- bounded retry of transient read-only GitHub verification calls only;
- timeline storage of remediation identity, branch, commit, PR, validation and reuse state.

A horizontally scaled production deployment should move this state to shared transactional storage without weakening the exact-proposal semantics.

## Evaluation follow-on is also complete

The previously planned follow-on Evaluation Lab now exists at `/evaluation` and measures the displayed deterministic benchmark cases rather than showing fabricated headline accuracy.

It covers routing, retrieval hit/no-match behavior, RCA grounding, risk policy, unsafe-action blocking, approval-gate behavior and measured validation success with visible numerators/denominators. Results are explicitly scoped to the benchmark cases and are not presented as universal real-world accuracy.

## Current verification record

The latest confirmed green `agent-build-core` branch head is:

```text
6ab99e02a5fc1911f2f0a75819ebf0cbb4661818
```

GitHub Actions **Build and test #983** / run ID `34713022064` completed successfully on 2026-09-12 with all three workflow jobs green:

```text
backend:             SUCCESS — constrained dependency install, resolved-version record, compile, tests and deterministic RAG/RCA smoke PASS
frontend:            SUCCESS — locked dependency install, resolved-version record and TypeScript/Vite build PASS
windows-clean-clone: SUCCESS — launcher syntax, PID safety, preflight, bootstrap and acceptance PASS
```

Build #983 re-verifies the refreshed GitHub Actions runtimes (`actions/checkout@v6`, `actions/setup-python@v7`, `actions/setup-node@v7`), reproducible backend install path, and the current paginated CI-evidence hardening on the exact recorded branch head. Direct backend requirements remain pinned, transitive versions are constrained in `backend/constraints.txt`, clean bootstrap refuses unconstrained backend installation, CI consumes the same files, and the resolved package set is recorded for auditability. Frontend installs continue through the committed lockfile.

The latest functional security hardening remains `4a37152ea1ec5c500f3599d89510035955985874`; later commits refresh release evidence, CI runtime maintenance, dependency reproducibility and CI-evidence integrity without expanding product authority.

The verified functional state includes fail-closed CI/check-state handling, full check-run pagination before status derivation, pagination drift/incompleteness safe-stop behavior, Draft-PR-head binding, adversarial-evidence/redaction hardening, bounded transient retry handling for idempotent GitHub verification reads, Evaluation Lab validation measurement, release-authority regression guards, deterministic RAG/RCA smoke coverage in CI and clean-clone acceptance, explicit Judge Intake labels for live-model versus fallback/guidance states, a repeatable validation-prep path that proves all registered demo FAIL → PASS contracts in isolated copies before restoring every live demo target to its intentional broken baseline, and normalized privileged-action screening that applies Unicode NFKC normalization and removes invisible Unicode format characters before policy matching. Regression coverage verifies Unicode-obfuscated merge/deploy instructions fail closed.

Older runs/head records, including #979, #977, #973, #969, #963, #959, #957, #951, #947, #943, #935, #879, #864, #819, #791, #789 and #632, are historical verification records only and should not be substituted for the current branch-level release evidence.

## Release discipline

The remediation milestone is closed. Do not add broad remediation scope before submission. Continue only with verified regressions, evidence-quality improvements, actual-device rehearsal and documentation polish.

`main` remains outside this branch's write scope and promotion remains manual.
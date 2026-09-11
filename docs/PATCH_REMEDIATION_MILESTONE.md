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

Supported backend/Python changes run compile and pytest in a fresh clone using the trusted project validation environment.

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
- timeline storage of remediation identity, branch, commit, PR, validation and reuse state.

A horizontally scaled production deployment should move this state to shared transactional storage without weakening the exact-proposal semantics.

## Evaluation follow-on is also complete

The previously planned follow-on Evaluation Lab now exists at `/evaluation` and measures the displayed deterministic benchmark cases rather than showing fabricated headline accuracy.

It covers routing, retrieval hit/no-match behavior, RCA grounding, risk policy, unsafe-action blocking and approval-gate behavior with visible measured numerators/denominators. Results are explicitly scoped to the benchmark cases and are not presented as universal real-world accuracy.

## Current verification record

The release-candidate documentation and safety-restored executable path are covered by the latest confirmed green push workflow before this documentation refresh:

```text
e743e1c22b71525f87ce5fac555ddbe0c40fceb6
```

GitHub Actions **Build and test run #791** / run ID `34644314306` completed successfully with all three workflow jobs green:

```text
backend:             SUCCESS
frontend:            SUCCESS
windows-clean-clone: SUCCESS
```

The prior executable code head `8c7ab3357af3365bff896397955e779db2847e25` was also fully green in run #789 with 109 backend tests passing, frontend locked install/build passing, Windows launcher/PID/preflight/bootstrap checks passing, clean-clone acceptance passing and the release contract passing.

Do not substitute older run #632 / head `a9221524011c2609e718bc1e3c6505445d5a90d6` as the current release evidence; that record is historical only.

## Release discipline

The remediation milestone is closed. Do not add broad remediation scope before submission. Continue only with verified regressions, evidence-quality improvements, actual-device rehearsal and documentation polish.

`main` remains untouched and promotion remains manual.

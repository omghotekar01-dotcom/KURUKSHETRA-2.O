# Patch Remediation Milestone

Date: 2026-09-11
Branch: `agent-build-core`

## What is now real

The live MVP can move from repository evidence to an approval-gated code remediation workflow:

```text
Incident
→ live GitHub evidence
→ ranked diff hunk + bounded source context
→ exact patch proposal
→ human APPROVE / REJECT
→ live proposal revalidation
→ isolated `incident-fix/...` GitHub branch
→ apply only the exact approved before/after replacement
→ re-read branch content to verify patch integrity
→ run deterministic local checks for supported code types
→ create a DRAFT pull request only when validation passes
```

## Safety boundaries

- No repository write occurs during investigation or patch-proposal generation.
- Rejection creates no branch, commit or PR.
- Approval is tied to the exact proposal object reviewed by the human.
- Before writing, the backend regenerates the proposal from fresh GitHub evidence and requires the exact proposal ID, file, hunk, before-lines and after-lines to match.
- The default-branch file is re-read immediately before the write. Missing or ambiguous source sequences fail closed.
- Every approved change is isolated on a dedicated `incident-fix/...` branch.
- Only the exact approved line sequence is replaced.
- The written branch file is re-read and byte-equivalent content is checked before validation.
- A draft PR is created only if all configured validation checks pass.
- No automatic merge or production deployment exists.

## Validation behavior

Supported frontend changes run a real dependency install plus production build in a fresh clone of the isolated branch.

Supported backend/Python changes run compile and pytest in a fresh clone of the isolated branch using the running backend environment.

Documentation-only changes use exact branch-content integrity validation because no executable code test is relevant.

Unknown executable code types fail closed until a trusted deterministic validator is configured.

## Live authentication

Repository writes require a configured `GITHUB_TOKEN` or an authenticated GitHub CLI session exposed through the existing credential adapter. Missing credentials return `AUTH_REQUIRED`; they never silently fall back to simulated success.

## Operator UI

`/remediate` now exposes the Remediation Studio with:

- incident selection,
- live repository inspection,
- safest eligible patch candidate,
- exact current/replacement lines,
- diff preview,
- proposal confidence and verification plan,
- human reviewer and note,
- explicit Reject and Approve actions,
- long-running validation state,
- isolated branch link,
- real validation results,
- draft PR link when the gate passes.

## Confirmed CI for implementation

GitHub Actions run #170 on implementation head `a8bab7a16e586c502d84fc02ed0741c1185fb0b1` completed successfully:

- backend compile: PASS
- backend tests: 36 passed, 0 failures
- frontend install: PASS
- frontend TypeScript/Vite production build: PASS

The test suite includes exact-sequence replacement, ambiguous-write rejection, validator selection and missing-auth fail-closed behavior in addition to the previous repository-evidence and patch-proposal coverage.

## Next milestone

Derive incident verification from actual remediation results and CI/check state, then build the repeatable Evaluation Lab / judge-facing scorecard.
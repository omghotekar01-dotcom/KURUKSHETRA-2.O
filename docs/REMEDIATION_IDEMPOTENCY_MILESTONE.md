# Remediation Idempotency Milestone

Date: 2026-09-11
Branch: `agent-build-core`
Project: **AI Agentic Bug Router**

## Why this exists

A real remediation product must be safe when a reviewer double-clicks Approve, refreshes the browser, retries after a timeout, or repeats a request after GitHub has already accepted part of the operation. A repeated approval must not silently create multiple fix branches, duplicate commits, or duplicate pull requests.

## Implemented behavior

### Stable execution identity
- Every exact incident + patch proposal receives a deterministic `REM-...` idempotency key.
- The fingerprint includes incident ID, proposal ID, repository, investigated commit, file, hunk, current lines and replacement lines.
- Changing the approved replacement changes the idempotency key.

### In-process duplicate serialization
- Approval requests for the same exact remediation are serialized with a per-idempotency-key lock.
- After acquiring the lock, incident state is re-read before any GitHub mutation.
- If an identical successful `PATCH_EXECUTION` already exists in the audit timeline, the previous result is returned and a `PATCH_EXECUTION_REUSED` event is added.

### Deterministic branch reuse
- Fix branches use the stable name `incident-fix/<incident>-<proposal>`.
- Random timestamp suffixes are no longer used as a duplicate fallback.
- If the deterministic branch does not exist, it is created from the current default-branch head and immediately re-read.
- If a retry finds the branch already created but still unchanged from its base, execution can safely continue by applying the exact approved replacement.
- If a retry finds the branch already containing the exact approved replacement, the branch is reused without a second write.
- If the branch exists with any other content, execution fails closed rather than overwriting or creating another branch.

### Pull-request reuse
- Before opening a pull request, the backend searches existing PRs for the deterministic remediation branch.
- An existing open PR is reused instead of creating a duplicate.
- If the matching remediation PR is already closed, the system fails closed and asks for review rather than silently opening another PR.

### Validation remains mandatory
- Branch reuse does not bypass deterministic validation.
- Frontend/backend validation still runs before a new Draft PR can be created.
- A successful duplicate approval that already has a recorded Draft PR returns the previous validated result without repeating repository writes.

### Auditability
`PATCH_EXECUTION` metadata now records:
- proposal ID
- idempotency key
- branch and branch URL
- commit SHA
- Draft PR number and URL
- validation results
- whether an existing GitHub resource was reused

Duplicate successful approvals additionally record `PATCH_EXECUTION_REUSED`.

## Safety boundary

This milestone does **not** add automatic merging or deployment. All code-changing actions remain tied to an exact reviewed patch proposal, an allowlisted repository and explicit human approval. Ambiguous or conflicting retry state fails closed.

## Confirmed validation

GitHub Actions run **#240** on implementation head `efe41371178733c0a1867aa243ba8d83e12968ea` completed successfully after the retry-safe path and its regression tests were added.

```text
Backend compile: PASS
Backend tests: 51 passed, 2 dependency deprecation warnings, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite production build: PASS
Overall workflow: SUCCESS
```

Regression coverage includes:
- deterministic idempotency-key generation
- changed proposal → changed key
- deterministic remediation branch naming
- existing PR lookup
- reconstruction of a previous successful execution
- fresh deterministic branch creation followed by safe re-read and exact write
- retry with already-patched branch + existing PR performs zero extra branch/commit/PR writes

## Next milestone

Reproducible startup and clean-clone acceptance:

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

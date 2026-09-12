# Release Status

Project: **KURUKSHETRA 2.0 — AI Agentic Bug Router**  
Project ID: **KH059**

## Current state

The startup-grade hackathon MVP is feature-complete for the final demonstration scope. The public release target is `main`.

The implemented product includes:

- incident intake, persistence, triage and routing;
- curated RAG plus verified resolution memory;
- live GitHub commits/issues/diffs/source context;
- suspicious-hunk ranking and evidence-backed RCA;
- isolated judge-supplied file/test intake;
- local Ollama/Qwen grounded proposals with bounded output;
- exact no-write patch preview;
- explicit human APPROVE / REJECT;
- stale-state and idempotency protections;
- isolated remediation branch creation;
- deterministic validation before Draft PR creation;
- live CI/check-status verification;
- repeatable Evaluation Lab metrics;
- readiness probes for Qwen and GitHub permission state;
- fail-closed handling for weak evidence, unavailable integrations and unsafe state.

## Authority boundary

```text
reviewed exact patch
→ isolated fix branch or isolated intake copy
→ deterministic validation
→ Draft PR when green
→ real GitHub CI/check evidence
→ external human repository review/merge
→ runtime/human verification
```

The model can reason and propose. Evidence, validators and explicit human approval control writes and verification. The application does not auto-merge and does not deploy production.

## Verification

The latest confirmed green `agent-build-core` head is commit `d924233da143bd17dcb9b490e397a4e648745429`, validated by GitHub Actions **Build and test #989** / run ID `34719104189` on 2026-09-12.

All three workflow jobs completed successfully:

- frontend locked dependency install + resolved-version record + TypeScript/Vite production build: PASS
- backend constrained dependency install + resolved-version record + compile + backend tests + deterministic RAG/RCA smoke: PASS
- Windows launcher syntax checks: PASS
- stale/reused PID safety checks: PASS
- environment preflight: PASS
- clean-checkout bootstrap/acceptance: PASS

Build #989 verifies the release workflow with the current GitHub Actions runtimes (`actions/checkout@v6`, `actions/setup-python@v7`, `actions/setup-node@v7`), reproducible backend dependency constraints, the paginated CI-evidence hardening, and the latest prompt-injection audit-detection hardening. GitHub check-runs are read across all API pages before deriving CI state, so a later-page failure cannot be hidden by first-page evidence. Inconsistent or incomplete pagination fails closed instead of producing PASS.

Direct backend dependencies remain pinned in `backend/requirements.txt`, transitive versions are constrained in `backend/constraints.txt`, clean bootstrap refuses unconstrained backend installs, CI installs through both files, and the resolved Python package set is recorded in the backend job. Frontend installs remain lockfile-based and CI records their resolved versions as well.

The latest product-security hardening is commit `d924233da143bd17dcb9b490e397a4e648745429`. In addition to the existing normalized privileged-action policy scan, untrusted-evidence prompt-injection audit detection now applies Unicode NFKC normalization and removes invisible Unicode format characters before signal matching. Regression coverage includes compatibility/fullwidth text and zero-width-character obfuscation while preserving the original evidence text for auditability.

The verified functional state also preserves a reliable judge-demo starting state: `REPAIR_VALIDATION.bat` proves every registered demo contract in isolated copies and then explicitly restores each live demo target to its intentional broken baseline before the demonstration begins. No benchmark score is inferred from CI; Evaluation Lab numbers remain separately measured from the displayed benchmark cases.

## Demo-critical proof surfaces

### `/prototype`
Controlled local regressions demonstrate real failing tests, bounded diagnosis, exact preview, real file edit, same-validator rerun and rollback on failure.

### `/intake`
Judge-supplied files are copied into an isolated workspace. Trusted pytest is opt-in. `VERIFIED_FIXED` requires a real FAIL → PASS transition using the same supplied test contract. Live-model, deterministic fallback and guidance-only states are visibly distinguished.

### `/evidence`
Live repository evidence exposes commits, changed files, suspicious diff hunks and bounded source context. Correlation is investigation guidance, not causal proof.

### `/remediate`
Exact proposals remain read-only until explicit approval. Approved remediation uses an isolated branch, exact-state checks, predefined validation and Draft PR creation only when validation is green.

### `/evaluation`
Benchmark results are computed from the displayed benchmark cases and are not presented as universal real-world accuracy.

### `/readiness`
Active probes distinguish configured/installed integrations from integrations that are actually callable and authorized.

## Release safeguards

- `.env` is not tracked;
- credentials are not returned by readiness APIs;
- recognized secret patterns are redacted from normal evidence surfaces;
- uploaded/repository text is treated as untrusted data;
- privileged-action checks normalize Unicode compatibility forms and strip invisible format characters before policy matching;
- untrusted-evidence prompt-injection audit detection normalizes Unicode compatibility forms and strips invisible format characters before signal matching while retaining original evidence text;
- repository writes are allowlisted and approval-gated;
- stale patches fail closed;
- generic Judge Intake does not invent a patch when the grounded model path is unavailable;
- CI check-runs are collected across all GitHub API pages before status derivation, and pagination drift/incompleteness fails closed;
- CI failure/pending/unknown states are not treated as success;
- CI PASS does not automatically resolve the original runtime incident.

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

The latest confirmed green `agent-build-core` head is commit `212343f9462f356fa563452013500ec394766f04`, validated by GitHub Actions **Build and test #959** / run ID `34695416678` on 2026-09-12.

All three workflow jobs completed successfully:

- frontend locked dependency install + TypeScript/Vite production build: PASS
- backend compile + backend tests + deterministic RAG/RCA smoke: PASS
- Windows launcher syntax checks: PASS
- stale/reused PID safety checks: PASS
- environment preflight: PASS
- clean-checkout bootstrap/acceptance: PASS

Build #959 re-verifies the release workflow with the current GitHub Actions runtimes (`actions/checkout@v6`, `actions/setup-python@v7`, `actions/setup-node@v7`) while preserving the same frontend, backend and Windows acceptance gates.

The latest product-security hardening remains commit `4a37152ea1ec5c500f3599d89510035955985874`; subsequent commits refresh release evidence/documentation and CI runtime maintenance rather than expanding product authority. Build #959 re-ran the complete release workflow on the exact branch head, so the branch-level release record supersedes #957, #951, #947, #943, #935, #879, #864 and #841.

The verified functional state includes normalized LLM policy scanning: Unicode NFKC normalization plus removal of invisible Unicode format characters occurs before privileged-action checks, and regression coverage confirms Unicode-obfuscated merge/deploy instructions fail closed to the deterministic path. The current head also preserves a reliable judge-demo starting state: `REPAIR_VALIDATION.bat` proves every registered demo contract in isolated copies and then explicitly restores each live demo target to its intentional broken baseline before the demonstration begins. No benchmark score is inferred from CI; Evaluation Lab numbers remain separately measured from the displayed benchmark cases.

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
- repository writes are allowlisted and approval-gated;
- stale patches fail closed;
- generic Judge Intake does not invent a patch when the grounded model path is unavailable;
- CI failure/pending/unknown states are not treated as success;
- CI PASS does not automatically resolve the original runtime incident.

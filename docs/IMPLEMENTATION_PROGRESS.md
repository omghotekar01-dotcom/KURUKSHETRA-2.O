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

The latest confirmed green `agent-build-core` release-candidate head is commit `f6002cdeebf3476feb571fdcfce8960fb955867b`, validated by GitHub Actions **Build and test #879** / run ID `34670772303` on 2026-09-12.

All three workflow jobs completed successfully:

- frontend locked dependency install + TypeScript/Vite production build: PASS
- backend compile + backend tests + deterministic RAG/RCA smoke: PASS
- Windows launcher syntax checks: PASS
- stale/reused PID safety checks: PASS
- environment preflight: PASS
- clean-checkout bootstrap/acceptance: PASS

This verification supersedes older release-candidate records such as Build #864 and #841 for the current branch state. The current head also includes explicit judge-intake labeling that distinguishes grounded live-model proposals, deterministic fallbacks and guidance-only fallback states without presenting fallback guidance as a live-model patch. No benchmark score is inferred from CI; Evaluation Lab numbers remain separately measured from the displayed benchmark cases.

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
- repository writes are allowlisted and approval-gated;
- stale patches fail closed;
- generic Judge Intake does not invent a patch when the grounded model path is unavailable;
- CI failure/pending/unknown states are not treated as success;
- CI PASS does not automatically resolve the original runtime incident.

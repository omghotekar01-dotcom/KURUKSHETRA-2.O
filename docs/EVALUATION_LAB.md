# Evaluation Lab

Date: 2026-09-11
Project: **AI Agentic Bug Router**
Branch: `agent-build-core`
Benchmark version: `2026.09.11-v1`

## Purpose

The Evaluation Lab gives judges and developers a repeatable way to verify the deterministic core instead of relying on screenshots or claimed accuracy numbers.

The runner executes fixed benchmark cases against the same production functions used by the MVP and computes every displayed metric at request time.

## What it measures

- **Routing accuracy** — whether representative Authentication, Database, Backend, Frontend and Infrastructure bugs route to the expected component/team.
- **Evidence retrieval hit rate** — whether the expected runbook appears in the top deterministic retrieval results.
- **RCA evidence grounding** — whether the root-cause hypothesis cites the expected evidence rather than making an unsupported claim.
- **No-match escalation** — whether an unknown incident remains unmatched and is escalated for human investigation.
- **Risk-policy accuracy** — whether low-, medium- and high-risk actions receive the expected policy.
- **Unsafe-action block rate** — whether destructive/production actions remain recommendation-only.
- **Approval-gate correctness** — whether bounded shared-state changes require human approval.

## API

```text
GET /api/v1/evaluation/run
```

The response contains:

- benchmark version and generation time,
- each metric with numerator/denominator,
- every benchmark case with expected and observed behavior,
- a simple mean score across the displayed metric ratios,
- explicit truth-boundary notes.

## UI

Open:

```text
/evaluation
```

The Light-theme judge-facing scorecard automatically runs the benchmark and displays:

- measured overall score,
- metric cards,
- individual PASS/FAIL benchmark evidence,
- category filtering,
- benchmark version and timestamp,
- a `Run benchmark again` control,
- explicit notes that the score is not an industry benchmark and that live GitHub remediation is validated separately.

## Truth boundary

No metric is hard-coded into the frontend. The score is computed from the benchmark results returned by the backend on each run.

The benchmark intentionally covers the deterministic local core. Live GitHub repository investigation, branch mutation, Draft PR creation and GitHub Actions verification depend on external repository state and remain covered by their own integration/unit tests and live workflow evidence.

## Latest code validation

GitHub Actions run #222 on head `3bf72f7d5a71800c5d9dc8b36b18be339b8657a5` completed successfully:

```text
Backend compile: PASS
Backend tests:   44 passed, 0 failures
Frontend install: PASS
Frontend TypeScript/Vite production build: PASS
```

The benchmark runner has dedicated tests for report structure, unsafe-action blocking and intentional no-match escalation. The full existing regression suite remains green.

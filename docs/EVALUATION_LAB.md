# Evaluation Lab

Date: 2026-09-12
Project: **AI Agentic Bug Router**
Branch: `agent-build-core`
Benchmark version: `2026.09.12-v2`

## Purpose

The Evaluation Lab gives judges and developers a repeatable way to verify the deterministic core instead of relying on screenshots or claimed accuracy numbers.

The runner executes fixed benchmark cases against production routing/retrieval/RCA/risk functions and now also executes a real isolated trusted-test validation contract. Every displayed metric is computed when `GET /api/v1/evaluation/run` runs.

## What it measures

- **Routing accuracy** — whether representative Authentication, Database, Backend, Frontend and Infrastructure bugs route to the expected component/team.
- **Evidence retrieval hit rate** — whether the expected runbook appears in the top deterministic retrieval results.
- **RCA evidence grounding** — whether the root-cause hypothesis cites the expected evidence rather than making an unsupported claim.
- **No-match escalation** — whether an unknown incident remains unmatched and is escalated for human investigation.
- **Risk-policy accuracy** — whether low-, medium- and high-risk actions receive the expected policy.
- **Unsafe-action block rate** — whether destructive/production actions remain recommendation-only.
- **Approval-gate correctness** — whether bounded shared-state changes require human approval.
- **Validation success** — whether the same trusted pytest contract demonstrably fails against a controlled broken state and passes after the bounded repaired state.

## Real validation benchmark

The validation metric is not a constant and is not inferred from a claimed patch result.

For the current controlled authentication fixture, the evaluator:

```text
create isolated temporary directory
→ write trusted test contract
→ write known broken source
→ run python -m pytest -q
→ require baseline exit != 0
→ replace only the controlled fixture source with the bounded repaired state
→ run the same python -m pytest -q contract again
→ require repaired exit == 0
→ record both exit codes and bounded validator output
```

The temporary directory is destroyed after the case. The benchmark does not write to the repository, create branches/PRs or execute model-generated shell commands.

The endpoint therefore reports `validation_success_rate` from an actual FAIL → PASS validator transition. If the baseline unexpectedly passes or the repaired fixture fails, the case and metric fail visibly.

## API

```text
GET /api/v1/evaluation/run
```

The response contains:

- benchmark version and generation time;
- eight measured metric cards with numerator/denominator;
- 21 benchmark case results;
- every expected and observed behavior;
- validator exit codes/output for the controlled validation case;
- a simple mean score across the displayed metric ratios;
- explicit truth-boundary notes.

## UI

Open:

```text
/evaluation
```

The light-theme judge-facing scorecard automatically runs the benchmark and displays:

- measured overall score;
- metric cards including Validation success;
- individual PASS/FAIL benchmark evidence;
- category filtering;
- benchmark version and timestamp;
- a `Run benchmark again` control;
- explicit notes that the score is not an industry benchmark and that live GitHub remediation is validated separately.

## Truth boundary

No metric is hard-coded into the frontend. The score is computed from the benchmark results returned by the backend on each run.

The controlled validation fixture is deliberately local and deterministic so the score remains repeatable. It proves that the Evaluation Lab actually measures a validator transition; it does **not** claim that arbitrary defects are repaired successfully.

Live GitHub repository investigation, branch mutation, Draft PR creation and GitHub Actions verification depend on external repository state and remain covered by their own integration/unit tests and live workflow evidence.

## Latest code validation

GitHub Actions **Build and test #831** / run ID `34664079242` on executable head:

`e9a80e808ea4810f0588831df584f90c13ccceec`

completed successfully on 2026-09-12:

```text
Backend compile:                       PASS
Backend tests:                         121 passed, 2 dependency warnings, 0 failures
Frontend locked dependency install:   PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax validation:    PASS
Windows stale/reused PID safety test:  PASS
Windows strict environment preflight:  PASS
Windows clean-checkout bootstrap:      PASS
Windows clean-clone acceptance:        PASS
Overall workflow:                      PASS
```

The Evaluation Lab regression tests verify report structure, unsafe-action blocking, intentional no-match escalation, the real FAIL → PASS validation case and the API contract for the new metric. Evaluation tests reuse one measured report per test module to avoid repeatedly spawning validator subprocesses during CI; the actual `/api/v1/evaluation/run` endpoint remains live and re-measures the benchmark on each request.

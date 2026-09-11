# EXPERIMENT BACKLOG

This file converts ideas into falsifiable tests. Each experiment should answer a question that can materially change product scope, architecture or judge claims.

## Priority A — validate before/early implementation

### EXP-001 — Routing accuracy baseline

Question: Can the system correctly classify incidents into the intended engineering component/team?

Dataset: 20–40 hand-curated incidents across frontend, backend, database, auth/security, infrastructure and unknown.

Measure:
- top-1 routing accuracy;
- unclassified accuracy;
- confusion matrix.

Success target for demo claim: >= 90% on curated benchmark, with transparent dataset size.

### EXP-002 — Historical retrieval usefulness

Question: Does semantic retrieval return the correct known incident/runbook in top-k?

Measure:
- top-1 relevance;
- top-3 hit rate;
- false confident matches.

Compare:
- keyword baseline;
- embedding search;
- embedding + category filter.

### EXP-003 — Multi-hypothesis RCA versus single answer

Question: Does ranking 2–3 hypotheses reduce wrong confident RCA compared with a single generated answer?

Evaluate on incidents with intentionally misleading evidence.

Measure:
- top-1 RCA accuracy;
- top-3 inclusion;
- confidence on incorrect answers.

### EXP-004 — Evidence ablation

Question: Which evidence sources actually improve RCA?

Run same incidents with:
1. report only;
2. report + runbook;
3. report + runbook + recent commit;
4. report + all available evidence.

This helps avoid adding connectors that do not improve outcomes.

### EXP-005 — Risk gate safety

Question: Does policy correctly block dangerous actions?

Scenarios:
- create GitHub issue → LOW;
- create draft PR → MEDIUM;
- restart production database → HIGH;
- delete database records → HIGH;
- send team notification → LOW.

Success: 100% of defined HIGH-risk scenarios require/deny autonomous execution.

### EXP-006 — Verification loop

Question: Can the product distinguish a proposed fix from a verified fix?

Build at least 3 deterministic scenarios:
- fix succeeds and test passes;
- patch generated but test fails;
- action cannot be verified and is escalated.

## Priority B — judge-value experiments

### EXP-007 — Time-to-triage comparison

Compare manual scripted workflow versus system workflow for a small set of incidents.

Measure seconds to:
- category/team;
- likely root cause;
- recommended action.

Do not overclaim enterprise MTTR reduction from a tiny benchmark. Present as prototype benchmark.

### EXP-008 — Noisy evidence robustness

Add irrelevant log lines, unrelated commit and distracting historical incident.

Measure whether correct hypothesis remains top-ranked.

### EXP-009 — Novel incident guard

Give an incident with no useful runbook match.

Expected behavior:
- retrieval confidence low;
- system says historical match is weak;
- RCA confidence reduced;
- no confident copied fix;
- escalate or suggest next diagnostic.

### EXP-010 — External integration failure

Disable GitHub/Gmail/LLM one at a time.

Expected behavior:
- system does not crash;
- action is stored/previewed;
- demo remains navigable;
- clear degraded-mode indicator.

## Priority C — future/post-MVP

### EXP-011 — Structured memory versus plain text memory

Compare retrieval from structured incident metadata versus a text-only archive.

### EXP-012 — Human steering

Allow engineer to say “check recent auth deployment” mid-investigation and measure whether agent incorporates the hypothesis without losing prior evidence.

### EXP-013 — Evaluation regression suite

Create a command that runs all benchmark incidents and emits JSON summary. Use before merging major agent/prompt changes.

### EXP-014 — Agent prompt regression

Store prompt versions and compare metrics after modifications instead of judging prompts by one sample.

## Benchmark scenario template

```yaml
id: INC-001
title: JWT 401 after deployment
report: Users receive 401 after successful login after latest deployment.
category: authentication
severity: high
expected_retrieval:
  - runbook_auth_jwt_rotation
accepted_root_causes:
  - JWT signing secret mismatch between deployed nodes
forbidden_autonomous_actions:
  - production_restart
  - secret_rotation
expected_safe_actions:
  - create_issue
  - draft_pr
verification:
  type: simulated_test
  expected: pass
```

## Experiment reporting rule

For every experiment record:
- date;
- code/prompt version;
- dataset/scenarios;
- metric;
- result;
- failure examples;
- decision caused by the result.

Never report a benchmark without the sample size and test conditions.
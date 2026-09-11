# TESTING AND QA STRATEGY

Last updated: 2026-09-11
Status: **PROVISIONAL**

## Testing objective

Prove that the system behaves reliably across normal, edge and failure cases — not only one scripted demo.

## Test layers

### 1. Unit tests
Target deterministic logic:
- risk classification rules;
- status transitions;
- parsers/normalizers;
- similarity functions;
- validation schemas;
- utility functions.

### 2. API tests
Test:
- valid request;
- missing fields;
- malformed payload;
- unknown incident ID;
- external dependency failure;
- expected status codes/error envelope.

### 3. Agent/output validation tests
Ensure:
- structured output parses;
- enums stay valid;
- confidence remains 0–1;
- unknown category is allowed;
- low evidence can produce `INSUFFICIENT_EVIDENCE`;
- unsafe action is not silently executed.

### 4. RAG tests
Test:
- obvious known match;
- paraphrased match;
- no-match case;
- misleading near-match;
- category-filter edge case;
- retrieval latency.

### 5. Integration tests
Golden path:
```text
POST incident
→ triage
→ retrieve evidence
→ RCA
→ remediation
→ approval
→ bounded action
→ verification
```

### 6. Frontend tests
Verify:
- loading state;
- error state;
- empty state;
- result rendering;
- approval flow;
- failed action state;
- responsive dashboard basics.

### 7. End-to-end judge flow
At least one Playwright/manual scripted test should reproduce the exact judging demo.

## Minimum deterministic scenario suite

Maintain fixtures for:
1. Authentication — 401 after deployment.
2. Frontend — broken mobile layout.
3. Database — timeout/connection pool exhaustion.
4. Backend — 502/upstream failure.
5. Dependency — third-party API outage.
6. Infrastructure — resource/disk problem.
7. Novel incident — no runbook match.
8. Misleading evidence — similar symptom, different actual cause.

See `INCIDENT_TAXONOMY_AND_TEST_SCENARIOS.md`.

## Safety test cases

- high-risk action must be blocked/recommendation-only;
- medium-risk action must require approval;
- edited action invalidates previous approval;
- rejected action is not executed;
- prompt-injection-like issue text cannot override system/tool policy;
- external content cannot request secrets;
- protected branch actions remain forbidden.

## Quality gates before merge to `main`

P0 gates:
- app starts from documented setup;
- golden demo flow passes;
- no uncaught crash on standard fixtures;
- no secret committed;
- API/UI contract matches;
- at least basic negative tests pass;
- deterministic demo mode works;
- actual limitations documented.

## Metrics collection

Record actual measured values where possible:
- routing accuracy;
- retrieval Hit@1/Hit@K;
- RCA top-1/top-3 accuracy on fixtures;
- unsafe-action block rate;
- verification success;
- end-to-end latency;
- failure recovery success.

Never invent a metric for presentation.

## Bug severity for our own project

### Blocker
Prevents end-to-end demo or data loss/security issue.

### Critical
Major core function broken with no easy workaround.

### Major
Important feature degraded but demo can continue.

### Minor
Cosmetic/nonessential issue.

Fix order: Blocker → Critical → demo-visible Major → remaining.

## Regression discipline

Whenever an agent prompt, retrieval threshold, model or data schema changes, rerun the same deterministic scenario suite. Improvement on one case that breaks three others is not progress.

## Final QA checklist

- fresh clone works;
- all environment variables documented;
- demo fixtures committed where safe;
- no dead buttons;
- no fake success states;
- loading/error states visible;
- integration credentials not exposed;
- external action points to safe/demo target;
- screenshots reflect current build;
- README commands tested.
# 24-HOUR EXECUTION ROADMAP

Last updated: 2026-09-11
Status: **PROVISIONAL — START CLOCK WHEN PS IS FROZEN**

This roadmap is optimized for a four-person team and a working end-to-end submission, not maximum feature count.

## T+0:00 to T+0:30 — PS triage
- Capture exact PS text/ID and organizer constraints.
- Map mandatory inputs/outputs.
- Decide whether current agentic incident-response direction is GO / MODIFY / DROP.
- Identify judge-visible success condition.

Deliverable: one-page PS interpretation.

## T+0:30 to T+1:00 — Solution freeze
- Finalize product name/one-line pitch.
- Define target user.
- Define golden demo path.
- Classify features P0/P1/P2.
- Select practical stack.
- Freeze module boundaries.

Deliverable: architecture + scope freeze.

## T+1:00 to T+1:30 — Contracts + Git
- Finalize API/state/database contracts.
- Update `DATA_API_AND_STATE_CONTRACTS.md`.
- Assign four-person responsibilities.
- Confirm each branch is current from `develop`.
- Add skeleton only after architecture freeze.

Deliverable: everyone can work independently without guessing interfaces.

## T+1:30 to T+4:00 — Parallel foundations
Parallel work should produce:
- backend API skeleton + state models;
- frontend UI with schema-matching mocks;
- RAG/evidence pipeline on fixtures;
- integration/evaluation/demo fixtures as assigned.

Checkpoint: every person has pushed meaningful commits.

## T+4:00 to T+6:00 — First ugly end-to-end MVP
Required path:

```text
incident input
→ backend
→ triage
→ retrieval/evidence
→ RCA/remediation
→ frontend result
```

External action/approval may still be stubbed, but data contracts must work.

Checkpoint: no one starts P2 until this works.

## T+6:00 to T+9:00 — Core depth
Add highest-value P0/P1 capabilities:
- confidence/evidence provenance;
- risk gate;
- incident history;
- one real integration;
- error handling;
- structured outputs.

Checkpoint: demo can survive normal errors.

## T+9:00 to T+12:00 — Closed-loop action
Implement:
- approval UI/state;
- bounded real action;
- verification result;
- incident timeline/update.

Checkpoint: full closed loop works once.

## T+12:00 to T+15:00 — Differentiation
Choose only 1–2 memorable differentiators, e.g.:
- evidence graph;
- multiple hypotheses;
- GitHub change correlation;
- verified incident memory;
- evaluation lab.

Do not add several shallow integrations.

## T+15:00 to T+18:00 — Integration + regression
- Merge current work into `develop`.
- Run deterministic incident suite.
- Fix contract mismatches.
- Measure latency/accuracy.
- Test failure cases.

Checkpoint: integrated build is stable.

## T+18:00 to T+20:00 — Product polish
- UI polish only now.
- Improve loading/progress/error states.
- Add useful charts/metrics.
- Capture screenshots.
- Clean obvious debug clutter.

## T+20:00 to T+21:30 — Documentation
- README install/run.
- Architecture diagram.
- API/data docs.
- Actual feature list.
- Limitations.
- Evaluation results.
- Team contribution mapping.

## T+21:30 to T+22:30 — Pitch + demo
- Finalize demo script.
- Prepare judge Q&A.
- Rehearse handoff between speakers.
- Verify project story matches actual implementation.

## T+22:30 to T+23:15 — Fresh-clone test
On a clean directory/machine:
- clone repo;
- configure env;
- install dependencies;
- run app;
- run demo.

Fix missing setup immediately.

## T+23:15 to T+24:00 — Freeze + submission buffer
- No major architecture changes.
- Merge tested `develop` to `main`.
- Tag final release if appropriate.
- Verify submission URL/files.
- Keep 30–45 minutes buffer for platform/upload problems.

## Time-loss recovery rules

If >2 hours behind:
- cut P2 completely;
- keep one integration;
- prefer SQLite/local data;
- remove nonessential auth/animations;
- keep golden path.

If >4 hours behind:
- freeze architecture;
- use deterministic demo fixtures;
- focus on input → evidence → RCA → recommendation → approval/action result.

If external integration blocks >45 minutes:
- isolate it;
- implement schema-compatible fallback;
- move on.

## Feature freeze rule

Once final integration begins, a new feature is allowed only if:
- it directly improves judging value;
- it takes little time;
- it does not modify shared contracts significantly;
- rollback is easy.

Otherwise defer it to future scope.
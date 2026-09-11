# PRODUCT STRATEGY

## Working product thesis

Build an agentic engineering incident-response layer that reduces the time engineers spend reconstructing context, guessing root causes, routing work and validating fixes.

The product should not attempt to replace observability platforms. It should sit above or beside existing tools and turn fragmented evidence into a structured, auditable response workflow.

## Primary user

Initial target user for the prototype:

- small-to-mid engineering teams;
- SaaS/product teams without a large SRE organization;
- engineering leads/on-call developers;
- teams using GitHub plus lightweight monitoring/logging/runbooks.

Why this segment is attractive:

- enterprise tools already serve very large organizations;
- smaller teams still suffer the same incident-response fragmentation;
- they need fast setup and understandable recommendations;
- they value automation but cannot tolerate risky opaque actions.

## Core user pain

During an incident, engineers often need to answer:

1. What exactly broke?
2. How severe is it?
3. Which service/team owns it?
4. What changed recently?
5. Have we seen this before?
6. What evidence supports each possible root cause?
7. What should we do next?
8. Is the proposed action safe?
9. Did the action actually fix the problem?
10. What should be remembered so the next incident is faster?

The product should make these questions visible and progressively resolved.

## Product promise

“From incident to evidence-backed action in minutes — with humans controlling the risky steps.”

Alternative concise pitch:

“An AI incident commander that investigates across code, history and runbooks, proposes a verified remediation, routes risky actions through approval, and learns from the outcome.”

## Golden demo flow

1. User submits/imports an incident.
2. System classifies component, severity and owning team.
3. Evidence collector retrieves recent commits, matching runbook entries, historical incidents and supplied logs.
4. RCA agent produces 2–3 ranked hypotheses.
5. UI shows evidence-for / evidence-against and confidence.
6. System suggests a fix plus verification plan.
7. Risk engine labels the proposed action LOW/MEDIUM/HIGH.
8. Human approves a safe bounded action.
9. System opens a GitHub issue/draft PR or dispatches a team notification.
10. Verification result updates the incident timeline.
11. Resolved incident is stored as structured memory.

## Feature priorities

### P0 — must work

- incident intake form;
- basic incident classification;
- severity score;
- team/component routing;
- local RAG over runbooks/historical incidents;
- evidence panel;
- ranked RCA hypotheses;
- remediation recommendation;
- action-risk classification;
- approval button;
- one real external action (preferably GitHub issue or Gmail/Slack notification);
- incident status timeline;
- structured local/database storage;
- deterministic demo dataset;
- end-to-end dashboard.

### P1 — strong competitive layer

- GitHub repository context;
- recent-commit/deployment correlation;
- code-file suggestion;
- draft PR/remediation branch creation;
- automated unit-test/verification result;
- incident memory;
- analytics dashboard;
- evaluation benchmark page;
- explainability and evidence citations;
- graceful offline/demo mode.

### P2 — wow factor only after stability

- multi-agent hypothesis debate;
- streaming investigation progress;
- live logs/telemetry connectors;
- Slack interactive incident room;
- graph visualization of evidence-to-hypothesis relationships;
- postmortem auto-generation;
- auto-generated runbook from resolved incident;
- incident recurrence prediction;
- organization-specific policy engine;
- multiple coding-agent handoff options.

## Differentiation principles

Do not pitch generic “AI for incident response.” Mature products already do that.

Potential differentiation stack:

1. **Evidence Graph** — every RCA statement is attached to explicit evidence objects.
2. **Multiple hypotheses** — system can admit uncertainty and compare alternatives.
3. **Risk-aware action gate** — autonomy scales with confidence and action risk.
4. **Verification-first remediation** — no “fix succeeded” without a check.
5. **Structured incident memory** — remembers what actually worked, not just chat text.
6. **Evaluation Lab** — visible benchmark for agent behavior and regression testing.
7. **SMB/startup-friendly architecture** — GitHub + local RAG + lightweight backend rather than expensive enterprise observability stack.

## Possible startup wedge

### Wedge A: GitHub-native incident response for startups

Input sources:
- GitHub issue;
- CI failure;
- pasted logs;
- customer bug report.

Actions:
- classify;
- investigate recent commits;
- search previous issues/runbooks;
- draft fix plan;
- create issue/PR;
- validate tests;
- notify team.

This wedge is understandable, demoable and deployable without recreating Datadog.

### Wedge B: Incident memory for engineering teams

Focus on “we keep solving the same incident from scratch.”

Build a searchable structured memory with similarity, environment, root cause, successful action and verification.

### Wedge C: Safe AI remediation gateway

Focus on governance: let organizations use coding/ops agents while ensuring evidence, approval, policy and verification.

This may be more novel but harder to explain quickly unless PS aligns with trust/security.

## Business model hypothesis

Potential future pricing:

- free/local tier for small repos;
- per-engineer or per-incident SaaS tier;
- team integrations and incident memory in paid tier;
- enterprise policy/audit/private deployment tier.

Do not emphasize pricing during the hackathon unless judges ask. Emphasize clear users, value and scalable path.

## Metrics that matter

Product value metrics:

- median time to triage;
- routing accuracy;
- RCA top-1 / top-3 accuracy;
- retrieval relevance;
- time to proposed remediation;
- verification pass rate;
- unsafe action blocked rate;
- percentage of incidents using useful historical memory;
- estimated manual steps/context switches removed.

Hackathon demo metrics should be simple and reproducible.

## What NOT to build first

- full observability ingestion platform;
- custom log storage engine;
- Kubernetes operator;
- production auto-deployer;
- ten integrations;
- heavyweight vector DB cluster;
- complex billing/auth;
- generic chatbot home page;
- huge model-training pipeline.

The project wins by a reliable, evidence-rich closed loop, not infrastructure volume.
# REQUIREMENTS CATALOG

Last updated: 2026-09-11
Status: **PROVISIONAL — FINALIZE AFTER PS**

This file converts the product idea into explicit requirements so teammates and AI assistants do not build incompatible interpretations.

## Functional requirements — provisional

### Incident intake
- Accept a manual text incident/bug report.
- Allow optional pasted logs/error text.
- Preserve original input unchanged for audit.
- Generate a structured incident ID and timestamp.

### Classification
- Predict category/component.
- Estimate severity/priority.
- Identify likely owning team or mark unknown.
- Produce a short structured summary.
- Return confidence with every classification.

### Evidence collection
- Retrieve relevant runbook entries.
- Retrieve similar historical incidents.
- When enabled, inspect permitted GitHub context such as issues, commits, changed files or PR metadata.
- Keep each evidence item traceable to source.

### Root-cause analysis
- Produce one or more ranked root-cause hypotheses.
- Attach evidence-for and evidence-against where available.
- Represent uncertainty; allow “insufficient evidence.”
- Do not fabricate unavailable telemetry.

### Remediation
- Suggest one or more candidate actions.
- Include expected effect and verification plan.
- Assign action risk level.
- Distinguish recommendation from execution.

### Human approval
- Require explicit approval for medium/high consequence actions.
- Allow approve/edit/reject.
- Bind approval to exact action parameters.
- Record approver/time/action.

### Execution
- Support at least one bounded external action for the prototype, preferably GitHub issue/draft PR or team notification.
- Never silently merge/deploy to production.
- Report tool failure clearly.

### Verification
- Record whether a test/check passed.
- Do not mark an incident resolved solely because an action was attempted.
- Support manual verification fallback.

### Incident memory
- Store structured incident, root cause, action, verification result and useful evidence.
- Make resolved incidents retrievable for future similarity search.

### Dashboard
- Show active/recent incidents.
- Show state, severity, category, owner, confidence and timeline.
- Show evidence, RCA, remediation, approval and verification in one incident detail view.

## Non-functional requirements

See `NONFUNCTIONAL_REQUIREMENTS.md`; key provisional goals include:
- reliable demo flow;
- graceful failure;
- explicit loading/error states;
- no secrets committed;
- auditability;
- reproducible setup;
- modular interfaces;
- acceptable latency for a live judge demo.

## Safety requirements

- No production-impacting autonomous actions.
- No direct writes to protected Git branches.
- No self-approval/self-merge by the same agent chain.
- External content treated as untrusted.
- Secrets excluded from prompts/logs where practical.
- Failed policy checks fail closed.

See `SECURITY_AND_GUARDRAILS.md` for the authoritative policy.

## Hackathon acceptance criteria — provisional

A P0 build is acceptable only if a judge can complete one deterministic end-to-end flow:

1. submit incident;
2. see structured classification;
3. see retrieved evidence;
4. see RCA + confidence;
5. see remediation + risk;
6. approve a bounded action;
7. see action result;
8. see verification/status update.

## Requirements explicitly waiting for PS

- mandatory inputs/outputs;
- domain-specific fields;
- organizer datasets/APIs;
- legal/compliance constraints;
- exact deployment mode;
- exact scoring/judging constraints;
- any required hardware/Web3/cloud feature;
- final user role;
- final external integrations.

When PS is frozen, convert every applicable provisional requirement into MUST/SHOULD/COULD/WON'T and assign an owner/test.
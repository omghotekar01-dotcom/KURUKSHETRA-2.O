# PROBLEM SPACE, USERS AND PERSONAS

Last updated: 2026-09-11
Status: **PARTIAL / WAITING_FOR_PS**

## Working problem space

Software incidents are expensive because engineers spend time reconstructing fragmented context before they can even begin remediation. The information needed to understand an incident may be spread across bug reports, logs, recent commits, previous issues, runbooks, monitoring tools, team chat, deployment history and human memory.

The current project direction aims to reduce this reconstruction cost without giving an opaque AI unlimited authority.

## Pain categories

### 1. Triage delay
Teams lose time deciding category, severity, affected component and owner.

### 2. Context fragmentation
Relevant evidence exists, but across multiple systems.

### 3. Repeated investigation
Teams repeatedly solve similar incidents because historical fixes are poorly structured or hard to retrieve.

### 4. Weak explainability
An AI suggestion without visible evidence is hard to trust.

### 5. Risky automation
Fully autonomous remediation can create larger outages if the model is wrong.

### 6. Verification gap
Many systems stop at “recommended fix” without proving the incident improved.

### 7. Poor incident memory
The final verified root cause/action often does not become reusable structured knowledge.

## Provisional primary persona

### On-call engineer / product engineer

Goals:
- understand what broke quickly;
- avoid checking five tools manually;
- see evidence behind RCA;
- know what changed recently;
- get a safe next action;
- verify whether the action worked.

Frustrations:
- noisy alerts;
- incomplete bug reports;
- tribal knowledge;
- stale runbooks;
- unclear ownership;
- repeated incidents;
- opaque AI output.

Success condition:
- faster evidence-backed triage and remediation with no unsafe action executed silently.

## Secondary personas

### Engineering lead
Needs:
- incident overview;
- escalation visibility;
- audit trail;
- metrics on recurring incidents and time saved.

### SRE / DevOps engineer
Needs:
- deeper evidence;
- low false-positive rate;
- safe automation boundaries;
- strong verification and rollback thinking.

### Small startup CTO / technical founder
Needs:
- SRE-like capability without building a large operations team;
- low setup cost;
- GitHub-native workflow;
- understandable controls.

### Support / QA engineer
Needs:
- convert a vague customer complaint into structured engineering context;
- track whether engineering accepted/resolved it.

## Jobs to be done

- “When an incident arrives, help me understand what likely happened before I manually search every tool.”
- “When we have seen something similar before, show me the verified previous fix.”
- “When you recommend a remediation, show me evidence and risk.”
- “When an action can be automated safely, let me approve it without giving the agent unlimited access.”
- “After resolution, remember what worked so the next incident is faster.”

## User journey hypothesis

1. Incident arrives or is entered manually.
2. User sees classification/severity/owner.
3. Investigation begins and evidence appears progressively.
4. System presents ranked hypotheses, not only one answer.
5. User inspects supporting evidence and similar incidents.
6. System proposes remediation + verification plan.
7. User approves/edits/rejects consequential action.
8. System executes bounded action.
9. User sees verification and incident timeline update.
10. Resolution becomes searchable memory.

## Questions that must be resolved after PS release

- Is the primary user actually an engineer, support team, platform team, enterprise IT team, or another stakeholder?
- Does the PS mandate a specific industry/domain?
- Is the main pain routing, RCA, remediation, auditability, cost, speed, or reliability?
- Is code access allowed/expected?
- Are there mandated integrations/datasets?
- Is the system meant for internal teams, external customers or government/enterprise workflows?

Do not freeze persona assumptions until these answers are known.
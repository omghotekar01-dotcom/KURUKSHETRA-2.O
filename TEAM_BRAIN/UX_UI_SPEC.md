# UX / UI SPECIFICATION

Last updated: 2026-09-11
Status: **PROVISIONAL — FINALIZE AFTER PS**

## Product experience goal

A judge or engineer should understand the system within roughly 30 seconds without needing a long verbal explanation.

The UI should make the incident lifecycle visible:

```text
Report → Triage → Evidence → RCA → Remediation → Approval → Action → Verification
```

## Primary screens

### 1. Dashboard
Purpose:
- show system status and recent incidents;
- communicate product value immediately.

Suggested cards:
- total incidents;
- resolved;
- investigating;
- escalated;
- median triage time;
- optional resolution-rate metric.

Suggested table columns:
- incident ID;
- title;
- category;
- severity;
- status;
- assigned team;
- age/created time.

### 2. New Incident
Inputs:
- incident/bug description;
- optional logs/error text;
- optional environment/component hints;
- optional GitHub issue/repo context if final scope permits.

Required states:
- empty;
- validating;
- submitting;
- error;
- success.

### 3. Investigation Progress
Show visible progress instead of a blank spinner:
- triage complete;
- searching runbooks;
- checking historical incidents;
- checking repo context;
- generating hypotheses;
- preparing remediation.

### 4. Incident Detail
Recommended tabs/sections:
- Overview
- Evidence
- Root Cause
- Remediation
- Timeline

Overview should show:
- severity;
- category/component;
- owner;
- confidence;
- current status;
- concise summary.

### 5. Evidence Panel
Every evidence item should show:
- source type;
- source name/ID;
- relevance;
- timestamp where available;
- snippet;
- link if external and safe.

### 6. RCA Panel
Show multiple hypotheses when possible:
- hypothesis text;
- confidence;
- evidence for;
- evidence against;
- missing information.

Avoid a giant opaque paragraph.

### 7. Remediation + Risk Panel
Show:
- proposed action;
- expected impact;
- risk level;
- prerequisites;
- rollback/fallback;
- verification plan;
- approval requirement.

### 8. Human Approval Dialog
Must show exact action before approval.

Controls:
- Approve
- Edit
- Reject

Do not use vague button text such as “Continue” for consequential action.

### 9. Action Result
Show:
- tool/integration used;
- success/failure;
- external issue/PR/message ID or URL;
- timestamp;
- retry/escalation option if appropriate.

### 10. Verification / Resolution
Show:
- PASS / FAIL / INCONCLUSIVE;
- verification evidence;
- final incident status;
- what is stored into incident memory.

## Visual hierarchy

Use a professional dark or light technical dashboard, not a generic neon “AI” interface.

Priority hierarchy:
1. incident state;
2. severity/risk;
3. evidence and RCA;
4. action/approval;
5. supporting analytics.

## Color semantics

Keep semantic meaning consistent:
- red = critical/high-risk/failure;
- amber = warning/medium;
- green = verified/success;
- blue/purple = informational/AI process;
- neutral gray = inactive/unknown.

Do not rely on color alone; include text/icons.

## Explainability UX

A strong differentiator is not merely showing “confidence 87%.” Let users expand:
- why the hypothesis ranked highly;
- what evidence was used;
- what evidence conflicts;
- what is still unknown.

## Demo UX principle

The golden demo should require few clicks:

```text
New Incident
→ Submit deterministic case
→ Watch investigation progress
→ Open RCA
→ Approve bounded action
→ See action succeed
→ See verification/resolved state
```

## Demo mode indicator

If using deterministic/local fallback data, label it clearly as demo mode rather than pretending a live external system was queried.

## Accessibility / usability minimums

- readable font sizes;
- keyboard-accessible primary controls where practical;
- sufficient contrast;
- no critical data hidden only in hover;
- clear loading and error messages;
- responsive enough for judge laptop/tablet widths.

## Frontend architecture principle

Centralize API calls and shared types. Do not hardcode mock data throughout components. Use one mock/demo service matching the frozen API schema so it can be replaced by live API calls without rewriting the UI.

## Waiting for PS

Freeze after PS:
- final screen list;
- project branding/name;
- exact user workflow;
- mandatory input fields;
- whether repository/log upload is required;
- whether judge-facing analytics are needed;
- final visual theme.
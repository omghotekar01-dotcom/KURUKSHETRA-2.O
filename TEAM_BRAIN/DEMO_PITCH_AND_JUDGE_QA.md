# DEMO, PITCH AND JUDGE Q&A PLAYBOOK

Last updated: 2026-09-11
Status: **PROVISIONAL — FINALIZE AFTER PS AND WORKING BUILD**

## Demo objective

Prove that the system can move from a raw incident to a safer, evidence-backed action and verification faster than a manual workflow.

## Ideal 3-minute demo flow

### 0:00–0:20 — Problem
Show one realistic incident:
> “Users get 401 after today’s deployment.”

Explain in one sentence:
> Engineers normally jump between reports, code history, runbooks and chat before they can act.

### 0:20–0:50 — Intake + triage
Submit the incident and show:
- category/component;
- severity;
- owner;
- confidence.

### 0:50–1:20 — Evidence + memory
Show:
- similar historical incident;
- relevant runbook;
- optional GitHub/recent-change evidence;
- visible source/relevance.

### 1:20–1:50 — RCA
Show ranked hypothesis:
- likely root cause;
- confidence;
- evidence for/against;
- uncertainty if applicable.

### 1:50–2:15 — Remediation + safety
Show proposed action, risk level and verification plan.

### 2:15–2:35 — Human approval + real action
Approve one bounded action such as:
- create GitHub issue;
- create draft PR;
- send team alert.

### 2:35–2:50 — Verification
Show PASS/FAIL/INCONCLUSIVE and status update.

### 2:50–3:00 — Impact
Show one measured result from the benchmark/demo, not an invented marketing number.

## One-line pitch options

- “An AI incident commander that turns fragmented engineering evidence into a safe, verifiable action.”
- “From incident to evidence-backed action in minutes — with humans controlling risky steps.”

## Judge-facing differentiation

Do not say:
> “We use React, FastAPI, LangGraph and AI.”

Say:
> “Unlike a normal bug router or chatbot, the system gathers evidence, represents uncertainty, gates risky actions, performs a bounded real action and verifies the outcome.”

## Expected judge questions and answer framework

### What is actually novel?
Answer with 2–3 concrete differentiators, not “AI + RAG.” Candidate answers:
- evidence-backed multi-hypothesis RCA;
- risk-aware approval gate;
- verification before resolution;
- structured incident memory;
- lightweight startup-friendly setup.

### How is this different from Sentry/Datadog/PagerDuty?
Acknowledge that mature products already do advanced incident investigation. Position our prototype around the specific gap/wedge selected after PS — e.g. lightweight GitHub-native workflow, transparent evidence/uncertainty, safe action gateway, verified incident memory. Never claim they cannot do AI incident response.

### Why is this agentic?
Because it operates a stateful multi-step workflow, selects/retrieves evidence, invokes bounded tools, pauses for human approval when required, executes an external action and verifies the result. It is not just one text-generation call.

### What happens if the AI is wrong?
- confidence shown;
- multiple hypotheses where possible;
- low-confidence fallback/escalation;
- no high-risk autonomous execution;
- human approval;
- verification after action.

### Is the retrieved historical fix always correct?
No. Similarity is evidence, not proof. We show source/relevance and combine it with other evidence; low-confidence retrieval falls back to manual investigation.

### What data did you train on?
Prefer not to imply training if none was done. Explain that the prototype uses a pretrained LLM/embedding model plus curated runbooks/historical incident fixtures and retrieval. If no custom training occurred, say so clearly.

### How do you evaluate it?
Use the benchmark in `EVALUATION_FRAMEWORK.md`: routing accuracy, retrieval hit rate, RCA correctness, unsafe-action rejection, verification success and latency on repeatable incidents.

### What is real versus mocked?
Be explicit. Label live integrations and demo fixtures. A deterministic fallback is reliability engineering, not something to hide.

### Can it modify production?
Not in the hackathon prototype. High-risk operations are recommendation-only. Medium-risk actions require approval and are scoped to safe targets such as non-protected branches/draft PRs.

### Why would anyone pay?
Because the product targets expensive engineering time lost to context gathering, repeated incidents and coordination; the startup thesis is a lightweight workflow layer for teams without large SRE organizations.

### What if there is no historical match?
The system must say there is no strong match and continue with available evidence or escalate. It must not fabricate a runbook solution.

### How does it learn?
Resolved incidents are stored as structured verified memory — symptoms, actual root cause, successful action and verification — and become future retrieval candidates.

## Demo failure playbook

If live LLM fails:
- switch to labeled demo mode / prepared deterministic case.

If GitHub action fails:
- show generated action payload/draft and explain integration state; do not pretend it succeeded.

If internet fails:
- local corpus + local frontend/backend + deterministic incident should remain demonstrable if implemented.

If one workflow stage errors:
- show explicit failure/escalation state rather than crashing the UI.

## Pitch deck skeleton

1. Title + one-line promise
2. Pain / current workflow
3. Why existing workflows are fragmented
4. Product flow
5. Architecture
6. Evidence/RCA/safety differentiator
7. Live demo
8. Evaluation results
9. Startup/scalability path
10. Closing value proposition

## Finalization rule

After the working build exists, replace all generic statements with:
- actual screenshots;
- actual measured timings/accuracy;
- actual implemented integrations;
- exact PS mapping;
- exact feature list;
- exact limitations.
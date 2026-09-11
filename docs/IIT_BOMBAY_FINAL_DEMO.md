# IIT Bombay Final Demo — AI Agentic Bug Router

This is the preferred judge-facing flow for the final presentation. Keep the demo truthful: LIVE data is shown as LIVE, deterministic fallback is shown as fallback, and no repository write is performed without a separate human approval action.

## 1. Open these tabs before presenting

Use the exact dashboard URL printed by `start.bat`.

1. `/readiness` — prove integrations and safety state.
2. `/ai` — explain the AI system and run a problem-to-solution scenario.
3. `/demo` — controlled golden engineering workflow.
4. `/evidence` — live GitHub commits, diffs and source context.
5. `/remediate` — exact patch + approval gate.
6. `/evaluation` — measured benchmark results.

The shared left navigation now links all of these surfaces and highlights the active screen.

## 2. 20-second problem statement

> Engineering teams lose time after a bug because the report, historical fixes, source-code changes, ownership, remediation and verification live in different places. Our AI Agentic Bug Router turns one incident into an evidence-backed engineering workflow: route it, retrieve relevant knowledge, inspect the real repository, synthesize an RCA, prepare a bounded fix, require human approval, validate it, and use CI/runtime evidence before resolution.

## 3. Explain the AI architecture on `/ai`

Use the architecture strip on screen:

```text
Incident
→ deterministic triage / owner routing
→ RAG over runbooks + verified incident memory
→ live GitHub commits / diffs / bounded source context
→ optional evidence-constrained LLM synthesis
→ deterministic risk policy
→ human approval
→ exact patch / isolated branch
→ deterministic validation
→ Draft PR
→ CI + runtime verification
→ verified resolution memory
```

### What is actually AI/RAG

- RAG retrieves relevant local runbooks and previously verified resolution memory for the current incident.
- Live GitHub evidence is a separate source of truth: commits, changed files, suspicious diff hunks and bounded source context.
- If `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` are configured, an OpenAI-compatible LLM receives only the bounded retrieved evidence and can synthesize the RCA wording, next diagnostic and remediation wording.
- Repository text is explicitly treated as untrusted data in the LLM prompt. The model is instructed not to follow instructions embedded in code, logs, commit messages or retrieved text.
- If the LLM is missing, times out, returns invalid JSON or the provider fails, the same API path falls back to deterministic evidence reasoning.
- The API returns an `agent_trace` with the real mode: `LLM_RAG` or `DETERMINISTIC_RAG`, provider, model, retrieval sources and fallback reason.

### What the LLM is NOT allowed to control

The LLM does not set confidence scores, approve actions, choose risk policy, write to GitHub, merge, deploy, or decide verification success. Those remain deterministic or human-controlled boundaries.

Recommended line:

> “The model helps synthesize engineering reasoning, but authority stays outside the model.”

## 4. Recommended problem-to-solution demo

Use **JWT authentication regression** first.

Problem shown to judges:

```text
Users can sign in, but protected API requests immediately fail after an auth-related deployment.
Logs:
- JWT signature verification failed
- 401 unauthorized after authentication deployment
```

Click **Run this incident**.

Then walk through the five result cards:

1. **Triage & routing** — Authentication, owner, severity, deterministic confidence.
2. **Retrieval-augmented context** — show the runbook / verified-memory matches and their measured retrieval scores.
3. **Live repository evidence** — show the real repository, top commit and correlation score. Say clearly that correlation guides investigation and is not proof of causation.
4. **Agent RCA synthesis** — point at the `LLM + RAG ACTIVE` or `DETERMINISTIC RAG FALLBACK` label. Do not describe fallback as an LLM result.
5. **Safe solution path** — show remediation steps, verification requirement and human-approval policy.

Then open `/evidence` to inspect the actual commit/diff/source proof and `/remediate` to show the exact patch boundary.

## 5. Other judge scenarios

### Database pool exhaustion

Use when a judge asks whether the router only knows authentication bugs.

Problem:

```text
Write requests fail under peak traffic.
sqlalchemy.exc.TimeoutError: QueuePool limit reached
PostgreSQL connection pool exhausted
```

What to demonstrate:
- Database routing.
- RAG selects database knowledge instead of auth knowledge.
- RCA/verification changes with the problem domain.

### Frontend API contract regression

Problem:

```text
A dashboard view stops rendering after an API response shape change.
TypeError: cannot read properties of undefined
```

What to demonstrate:
- Frontend routing.
- Live changed-file / diff investigation.
- Verification is the affected user flow, not merely “build passed.”

### Infrastructure health regression

Problem:

```text
New replicas repeatedly restart after rollout.
readiness probe failed
container memory pressure
```

What to demonstrate:
- Infrastructure routing.
- Risk policy is stricter for production-impacting actions.
- The system never auto-deploys or performs destructive production operations.

### Unknown / no-match safe stop

Problem:

```text
A new Orion service changes payload fields intermittently with no trusted historical or repository context.
```

What to demonstrate:
- RAG reports no strong match.
- No root-cause hypothesis is fabricated.
- No remediation is invented.
- The workflow escalates for human investigation.

Recommended line:

> “A useful engineering agent needs to know when not to act.”

## 6. Live remediation flow

Only demonstrate live GitHub writes if auth is working and the exact proposal is understandable.

```text
Exact no-write patch proposal
→ human reviews before/after lines
→ Arm live remediation
→ explicit APPROVE
→ fresh stale-state validation
→ isolated incident-fix branch
→ exact approved replacement only
→ deterministic validation
→ Draft PR only if validation passes
→ real GitHub CI status
```

Never merge the Draft PR during judging.

## 7. Best 60-second complete sequence

1. `/readiness`: “Live-first, repo allowlisted, no auto-merge/deploy.”
2. `/ai`: choose JWT regression and click **Run this incident**.
3. Point at triage + RAG match + live repo evidence.
4. Point at the real agent mode (`LLM_RAG` or deterministic fallback).
5. Show RCA + next diagnostic + safe remediation.
6. `/evidence`: show commit/diff/source context.
7. `/remediate`: show exact patch and human approval gate, but do not write unless intentionally demonstrating it.
8. `/evaluation`: show measured benchmark results and say they apply to the displayed deterministic benchmark only.

## 8. Strong closing line

> “This is not an AI chatbot that guesses fixes. It is an auditable engineering control loop: retrieval, live code evidence, grounded reasoning, policy, human approval, validation, CI verification and reusable incident memory.”

## 9. Final safety rules

- Never expose a token or `.env` value on screen.
- Never call fallback/demo evidence live.
- Never say correlation proves causation.
- Never say CI PASS proves production recovery.
- Never auto-merge or deploy.
- Never force a patch when the system returns a safe stop.

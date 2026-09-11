# IIT Bombay Final Demo — AI Agentic Bug Router

This is the preferred judge-facing flow for the final presentation. The strongest proof is now `/prototype`: a genuinely broken local project is scanned, reproduced, edited and verified in real time. Keep every label truthful: local model use is shown as local model use, deterministic fallback is shown as fallback, and a repair is called FIXED only after the target's own validator passes.

## 1. Open these tabs before presenting

Use the exact dashboard URL printed by `start.bat`.

1. `/prototype` — **primary proof:** real broken workspace → failing test → source diagnosis → real edit → same test passes.
2. `/readiness` — integrations and safety state.
3. `/ai` — RAG/LLM reasoning architecture and broader incident scenarios.
4. `/evidence` — live GitHub commits, diffs and source context.
5. `/remediate` — GitHub-oriented exact patch + approval gate.
6. `/evaluation` — measured benchmark results.
7. `/demo` — controlled full engineering workflow.

The shared left navigation links all of these surfaces and highlights the active screen.

## 2. 20-second problem statement

> Engineering teams lose time because reproducing a bug, finding the responsible code, understanding historical context, making a safe fix and proving recovery happen in different tools. Our AI Agentic Bug Router turns one granted project workspace into a verified repair loop: reproduce the failure, ground the diagnosis in tests and source, let a free/local model propose a bounded patch, modify the real file, rerun trusted validation, roll back on failure, and preserve the result as reusable engineering knowledge.

## 3. Primary judge demo: `/prototype`

Use **Broken Bearer Authentication API**.

The target is a real project under:

```text
demo_targets/broken_auth_api/
```

Its client/test contract uses:

```text
Authorization: Bearer demo-valid-token
```

but the source incorrectly checks:

```python
if scheme.lower() != "token":
```

### Demo sequence

1. Click **Reset broken target**.
2. Click **1. Scan + reproduce**.
3. Show the actual `pytest` command, non-zero exit code and failure output.
4. Show the grounded diagnosis: `app.py`, exact line, Bearer-vs-Token mismatch and evidence.
5. Click **2. Preview exact fix**.
6. Point at the reasoning badge:
   - `AI GROUNDED PATCH · ollama-local · qwen3:4b` when local Qwen is available; or
   - `SAFE FALLBACK PATCH` when the model is unavailable/rejected.
7. Show the real unified diff before it writes anything.
8. Click **3. Auto Fix + Verify**.
9. Show **BEFORE FAIL → AFTER PASS** and the post-fix output from the same test suite.
10. Open the audit trail and explain that a failed candidate is restored automatically.

Recommended line:

> “This is not a screenshot or generated success message. That is a real broken FastAPI project, a real source-file edit and a rerun of its own test suite. The system is not allowed to say FIXED until the validator exits zero.”

### Why this proof matters

A judge can independently inspect `demo_targets/broken_auth_api/app.py`, run its tests manually, or compare the file before and after AutoFix. The product therefore demonstrates an observable engineering state transition rather than a simulated chat response.

## 4. Zero-cost AI setup

No paid API is required.

Default order:

```text
Local Ollama + qwen3:4b
→ optional Gemini Developer API free-tier key
→ deterministic evidence/repair fallback
```

Recommended laptop preparation:

```powershell
setup-local-ai.bat
```

or manually:

```powershell
ollama pull qwen3:4b
```

The application uses Ollama's OpenAI-compatible localhost endpoint. If Ollama is offline, the repair proof still runs through the deterministic source/test contract engine; the UI shows that fallback instead of pretending an LLM ran.

Gemini is optional only. Keep any `GEMINI_API_KEY` in the local `.env`; never commit it. Free-tier availability and quota remain provider-controlled.

## 5. Explain the architecture on `/ai`

Use this mental model:

```text
Incident / project failure
→ deterministic triage + validator evidence
→ RAG over runbooks + verified resolution memory
→ local workspace files and/or live GitHub evidence
→ optional Qwen/Gemma/Gemini grounded reasoning
→ bounded exact patch candidate
→ workspace/path policy
→ real file edit
→ predefined trusted validator
→ PASS = proven repair
→ FAIL = automatic rollback / alternate safe candidate
→ optional Draft PR + CI
→ runtime verification
→ verified resolution memory
```

### What the model can do

- synthesize RCA wording from bounded evidence;
- propose a tiny exact `search → replace` code patch using only files supplied to it;
- explain the candidate patch.

### What the model cannot do

- access arbitrary operating-system paths;
- select unrestricted shell commands;
- write outside the approved workspace;
- declare that tests passed;
- bypass stale-file checks;
- bypass rollback;
- merge or deploy automatically;
- decide runtime verification success.

Recommended line:

> “The model can reason and propose; evidence and validators hold authority.”

## 6. Workspace safety story

Do **not** describe the product as giving an LLM unrestricted control of the entire laptop. Describe it as startup-grade workspace autonomy.

Current boundary:

```text
Explicit workspace root
→ registered target folder
→ bounded readable source files
→ blocked secret/build/system directories
→ exact reviewed patch
→ predefined validator only
→ rollback on failure
```

The scanner blocks path traversal and excludes sensitive/build directories such as `.git`, `.ssh`, `.aws`, `.azure`, `.config`, virtual environments and `node_modules`.

That design lets a company grant the agent access to a repository/project without granting arbitrary OS authority.

## 7. Broader incident/RAG demonstration

After proving AutoFix, open `/ai` and use the JWT authentication regression or another scenario.

Show:

1. deterministic routing;
2. RAG runbook/verified-memory retrieval;
3. live GitHub evidence where available;
4. actual reasoning mode/provider/model;
5. grounded RCA;
6. safe remediation and verification plan.

Other available demonstrations include database pool exhaustion, frontend API contract regression, infrastructure health regression and an unknown/no-match safe-stop case.

For the unknown case, emphasize that the system refuses to fabricate a fix when evidence is insufficient.

Recommended line:

> “A useful engineering agent needs to know both how to repair and when not to act.”

## 8. GitHub remediation flow

Use `/evidence` and `/remediate` after the local proof if the judges want to see repository-scale operation.

```text
Live commit/diff/source evidence
→ exact no-write patch proposal
→ human review / approval
→ fresh stale-state validation
→ isolated incident-fix branch
→ exact approved replacement
→ deterministic validation
→ Draft PR only if validation passes
→ real GitHub CI
→ runtime proof still required
```

Never merge the Draft PR during judging.

## 9. Best 90-second complete sequence

1. `/prototype`: Reset broken target.
2. Scan + reproduce → show real pytest FAIL.
3. Show exact culprit source line and evidence.
4. Preview fix → point out `AI GROUNDED PATCH` or truthful safe fallback.
5. Auto Fix + Verify → show real FAIL → PASS.
6. `/ai`: explain local/free model + RAG + verified memory architecture.
7. `/evidence`: show real GitHub source evidence.
8. `/evaluation`: show measured benchmark results, clearly scoped to displayed benchmark cases.

If there is extra time, show `/remediate` and its approval/Draft-PR boundary.

## 10. Strong closing line

> “Most coding assistants generate an answer. We prove an engineering state transition: reproduce, ground, repair the granted workspace, validate the real code, roll back bad changes, and learn only from verified outcomes.”

## 11. Final safety/truth rules

- Never expose tokens or `.env` values on screen.
- Never call fallback evidence live AI.
- Never claim a model solved the bug if the UI says deterministic fallback.
- Never say commit correlation proves causation.
- Never say CI PASS alone proves production recovery.
- Never allow model-generated arbitrary shell execution.
- Never grant the model unrestricted whole-computer file access.
- Never auto-merge or production deploy.
- Never force a patch when evidence or validation fails.

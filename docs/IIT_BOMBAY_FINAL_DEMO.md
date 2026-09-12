# IIT Bombay Final Demo — AI Agentic Bug Router

This is the preferred judge-facing flow for the final presentation. Use two complementary proofs:

1. `/prototype` — a guaranteed repeatable real regression where the same validator fails before the reviewed edit and passes after it.
2. `/intake` — a judge/operator supplies the bug report and files, RAG retrieves relevant engineering knowledge, the configured local/free model proposes a bounded patch, and the system verifies or rolls back the isolated copy.

Keep every label truthful. Local-model use is shown as local-model use, deterministic fallback is shown as fallback, static-only validation is not called functional recovery, and a repair is called `VERIFIED_FIXED` only when a previously failing trusted test passes after the exact reviewed patch.

## 1. Open these tabs before presenting

Use the exact dashboard URL printed by `start.bat`.

1. `/prototype` — guaranteed real FAIL → reviewed edit → same-test PASS proof.
2. `/intake` — judge-supplied bug report + attached source/test files.
3. `/readiness` — integrations and safety state.
4. `/ai` — RAG/LLM reasoning architecture and broader incident scenarios.
5. `/evidence` — live GitHub commits, diffs and source context.
6. `/remediate` — GitHub-oriented exact patch + approval gate.
7. `/evaluation` — measured benchmark results.
8. `/demo` — controlled full engineering workflow.

The shared left navigation links these surfaces and highlights the active screen.

## 2. 20-second problem statement

> Engineering teams lose time because reproducing a bug, finding the responsible code, understanding historical context, making a safe fix and proving recovery happen in different tools. AI Agentic Bug Router turns a granted project workspace into a verified repair loop: reproduce or inspect the failure, retrieve relevant knowledge, ground reasoning in tests/source/repository evidence, preview a bounded patch, require review, rerun trusted validation, roll back bad changes, and preserve verified outcomes as reusable engineering knowledge.

## 3. Prove the model is really connected

Before any AI claim, prepare the laptop:

```powershell
setup-local-ai.bat
start.bat
```

`start.bat` now prints the detected AI runtime. For the intended offline-first demo, prefer:

```text
AI runtime: LIVE LOCAL QWEN (qwen3:4b)
```

Then open `/intake` and click **Test Qwen now**.

The button performs a real chat-completions request and displays:

- connected / unavailable;
- provider;
- model;
- latency;
- model reply.

Only describe Qwen as live when this probe succeeds. If Ollama is unavailable, built-in `/prototype` targets still have deterministic verified fallback, while arbitrary generic judge intake fails closed rather than inventing an AI patch.

Default model order:

```text
Local Ollama + qwen3:4b
→ optional Gemini free-tier fallback when configured
→ deterministic fallback for supported built-in proof targets
```

## 4. Guaranteed primary proof: `/prototype`

Use any registered broken target. Recommended first target: **Broken Bearer Authentication API**.

The real source/test mismatch is:

```text
client/test: Authorization: Bearer demo-valid-token
source:      scheme.lower() != "token"
```

### Demo sequence

1. Click **Reset broken target**.
2. Click **1. Scan + reproduce**.
3. Show the actual pytest command, non-zero exit code and failure output.
4. Show the grounded diagnosis and culprit file/line.
5. Click **2. Preview exact fix**.
6. Point at the real planner badge:
   - `AI GROUNDED PATCH · ollama-local · qwen3:4b` when Qwen produced the proposal; or
   - `SAFE FALLBACK PATCH` when deterministic source/test evidence produced it.
7. Show the unified diff before any write.
8. Click **3. Auto Fix + Verify**.
9. Show **BEFORE FAIL → AFTER PASS** from the same validator.
10. Open the audit trail and explain that a failed reviewed patch is restored automatically.

Recommended line:

> “This is a real broken project, a real source-file edit and a rerun of its own test suite. The system is not allowed to say FIXED until the validator exits zero.”

The repository also contains additional repeatable built-in targets for cart-total arithmetic and pagination regressions so the controlled proof is not limited to one authentication example.

## 5. Judge challenge: `/intake`

This is the answer to: **“Can I give you my own bug or files?”**

A judge can:

1. type the problem statement;
2. attach up to 12 allowlisted text/code files;
3. optionally enable **Trusted test execution** for files they trust;
4. click **1. Analyze files + retrieve RAG**;
5. inspect baseline validation and retrieved runbook matches;
6. click **2. Preview grounded AI fix**;
7. inspect the exact file/search/replace diff, provider and model;
8. click **3. Apply reviewed patch + verify**.

### What happens internally

```text
judge bug report + files
→ isolated temporary workspace
→ bounded file inventory
→ static baseline OR explicitly trusted pytest baseline
→ RAG over engineering runbooks
→ Qwen receives bounded bug/test/RAG/file evidence only
→ validated exact search/replace candidate
→ visible no-write Preview
→ one-time operator approval
→ exact reviewed edit inside isolated copy
→ same trusted validator or static validation
→ VERIFIED_FIXED / STATIC_CHECK_PASSED / ROLLED_BACK
```

### Strongest judge-supplied proof

Ask the judge to provide:

- a small Python source file;
- a `test_*.py` that currently fails;
- a clear expected/observed bug statement.

Enable **Trusted test execution** only if those files are trusted.

The strongest state transition is:

```text
trusted pytest BEFORE = FAIL
→ RAG evidence
→ Qwen exact reviewed patch
→ apply
→ same trusted pytest AFTER = PASS
→ VERIFIED_FIXED
```

If the judge supplies only source files, no trusted failing test exists. The system may produce a bounded patch and static validation, but the final label is only:

```text
STATIC_CHECK_PASSED
```

Do not call that functional recovery.

If Qwen is unavailable or rejects the evidence, generic intake shows no safe patch. That fail-closed behavior is intentional.

## 6. Why uploaded files are isolated

Do not say the model has unrestricted access to the laptop.

Judge-supplied files are copied into an ephemeral temporary session. Intake rejects traversal, absolute paths and sensitive/build directories. Qwen sees only bounded text supplied to the session. Writes stay inside that isolated copy.

User-supplied code is not executed by default. Python tests run only after explicit **Trusted test execution** opt-in.

Recommended line:

> “We give the agent workspace autonomy, not operating-system authority.”

## 7. Explain RAG + AI architecture on `/ai`

Use this mental model:

```text
incident / bug report
→ deterministic routing + baseline evidence
→ RAG: runbooks + verified resolution memory
→ local uploaded workspace and/or live GitHub evidence
→ optional live Qwen/Gemini grounded reasoning
→ exact bounded patch candidate
→ path/write policy
→ human review
→ trusted validation
→ PASS or rollback
→ optional Draft PR + CI
→ runtime verification
→ verified resolution memory
```

### Model can

- synthesize RCA wording from bounded evidence;
- propose a tiny exact code change using supplied files;
- explain the candidate patch.

### Model cannot

- access arbitrary OS paths;
- choose unrestricted shell commands;
- write outside approved/isolated workspaces;
- declare tests passed;
- bypass stale-file checks or approval;
- bypass rollback;
- merge or deploy automatically;
- decide runtime verification success.

Recommended line:

> “The model can reason and propose; evidence and validators hold authority.”

## 8. Broader incident/RAG demonstration

After the repair proof, use `/ai` for one known incident and one no-match case.

Show:

1. deterministic routing;
2. RAG retrieval;
3. verified-resolution memory when available;
4. live GitHub evidence where available;
5. actual provider/model/fallback mode;
6. grounded RCA;
7. safe remediation and verification plan.

For an unknown/no-match case, emphasize that the system refuses to manufacture supporting evidence.

## 9. GitHub evidence and remediation

Use `/evidence` and `/remediate` if judges want repository-scale operation.

```text
live commit/diff/source evidence
→ exact no-write patch proposal
→ human review / approval
→ fresh stale-state validation
→ isolated incident-fix branch
→ exact approved replacement
→ deterministic validation
→ Draft PR only after green validation
→ real GitHub CI/check evidence
→ runtime proof still required
```

Never merge the Draft PR during judging.

## 10. Best complete presentation sequence

### 90-second version

1. `/prototype`: Reset → Scan → real FAIL.
2. Preview exact diff.
3. Auto Fix → same validator PASS.
4. `/intake`: click **Test Qwen now** to prove live local model connectivity.
5. Briefly show that judges can type a bug and attach their own files.
6. `/evaluation`: show measured benchmark results.

### 3–5 minute version

1. `/intake`: Test Qwen now.
2. Let judge provide a small bug + source/test pair when practical.
3. Analyze + RAG.
4. Preview exact AI patch.
5. Apply + same trusted test PASS → `VERIFIED_FIXED`.
6. `/prototype`: use as guaranteed recovery demo if judge files are unsuitable or model/network conditions are bad.
7. `/evidence`: show real GitHub source evidence.
8. `/remediate`: show approval/Draft-PR boundary.
9. `/evaluation`: show measured scorecard.

## 11. Recovery strategy during judging

If something external fails:

- Qwen unavailable → show the failed live probe truthfully; use `/prototype` deterministic verified fallback.
- Judge gives unsafe/untrusted code → keep Trusted test execution off; use static-only analysis.
- Generic evidence too weak → accept the visible no-patch safe stop instead of guessing.
- GitHub/network unavailable → use local `/prototype` and `/intake`; label remote evidence unavailable.
- Port collision → use the exact URLs printed by `start.bat`.

A safe stop is better than a fabricated success.

## 12. Strong closing line

> “Most coding assistants generate an answer. We prove an engineering state transition: ingest real evidence, retrieve context, ground a bounded repair, require review, validate the real change, roll back failures, and learn only from verified outcomes.”

## 13. Final truth rules

- Never expose tokens or `.env` values on screen.
- Never call fallback evidence live AI.
- Never say Qwen ran unless the live probe or proposal provenance proves it.
- Never call `STATIC_CHECK_PASSED` a functionally verified repair.
- Never say commit correlation proves causation.
- Never say CI PASS alone proves production recovery.
- Never run arbitrary uploaded code without explicit trust.
- Never allow model-generated arbitrary shell execution.
- Never grant the model unrestricted whole-computer file access.
- Never auto-merge or deploy production.
- Never force a patch when evidence or validation fails.

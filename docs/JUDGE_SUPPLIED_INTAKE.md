# Judge-Supplied Bug Intake

The AI Agentic Bug Router now has two complementary real-repair surfaces:

- `/prototype` — repeatable built-in broken projects with deterministic safe fallback and real pytest FAIL → PASS proof.
- `/intake` — a judge/operator types a bug report and attaches their own source/test files for isolated RAG + grounded model analysis.

Neither surface is a simulation. Their proof strength is intentionally labeled differently.

## 1. Prove Qwen/Ollama is actually connected

Run on Windows from the repository root:

```powershell
.\setup-local-ai.bat
.\start.bat
```

`setup-local-ai.bat` now:

1. confirms `ollama` exists on PATH;
2. confirms the Ollama service is reachable or starts `ollama serve` in a minimized window;
3. pulls `qwen3:4b`;
4. confirms `qwen3:4b` appears in `ollama list`;
5. refuses to print READY if those checks fail.

Open the `Judge Intake` URL printed by `start.bat` and click **Test Qwen now**.

That button calls the backend model probe, which performs a real OpenAI-compatible `/chat/completions` request. The UI shows:

- connected / unavailable;
- provider;
- model;
- latency;
- returned probe text.

A model is not described as connected merely because an environment variable exists.

## 2. Judge-supplied file workflow

Open `/intake`.

1. Type the bug report: expected behavior, observed behavior, error/log, and useful reproduction detail.
2. Attach up to 12 text/code files (256 KB maximum per file).
3. Optionally enable **Trusted test execution** only if the supplied Python tests are safe to execute.
4. Click **1. Analyze files + retrieve RAG**.
5. Review the baseline validator evidence and retrieved engineering runbooks.
6. Click **2. Preview grounded AI fix**.
7. Review the exact file, explanation, provider/model and unified diff. No write has happened yet.
8. Click **3. Apply reviewed patch + verify**.
9. Inspect the final status and audit trail.

### Final status meanings

`VERIFIED_FIXED`

- trusted user-supplied pytest existed;
- that pytest failed before the patch;
- the exact reviewed patch was applied to the isolated copy;
- the same pytest passed afterward.

`STATIC_CHECK_PASSED`

- the reviewed patch was applied to the isolated copy;
- syntax/schema checks passed;
- no claim of functional recovery is made because a failing trusted functional test was not available.

`ROLLED_BACK`

- the candidate failed the selected validator;
- the original uploaded file was restored.

## 3. Safety boundary

Judge-supplied files are copied into an ephemeral session under the operating-system temporary directory. The generic intake does not write back into arbitrary folders on the laptop.

Blocked paths include traversal (`..`), absolute paths, Windows drive paths and sensitive/build directory names such as `.git`, `.ssh`, `.aws`, `.azure`, `.config`, virtual environments, `node_modules` and `__pycache__`.

The model receives bounded text only. Its output must validate as one exact JSON search/replace candidate:

```json
{
  "file_path": "one supplied file",
  "search": "one exact unique substring already in that file",
  "replace": "bounded replacement text",
  "explanation": "why this matches the supplied evidence"
}
```

The model cannot choose arbitrary shell commands, invent unsupplied file paths, mark tests passed, merge a PR or deploy production.

## 4. Trusted-test boundary

Uploaded code is not executed by default.

Default `STATIC_ONLY` mode performs bounded static validation. Python is compiled and JSON is parsed, but the application explicitly says that functional recovery is not proven.

When the operator explicitly enables **Trusted test execution** and the upload contains Python `test_*.py` files, the isolated session may execute:

```text
python -m pytest -q
```

with a reduced environment and a timeout. This is an operator trust decision, not an automatic action on arbitrary attachments.

## 5. RAG path

Generic intake retrieves matching engineering runbooks from the local curated knowledge base using the typed bug report plus bounded uploaded source evidence. The UI shows the actual matches and match scores; if there is no strong match, it says so instead of fabricating one.

The broader incident workflow under `/ai` also uses verified resolution memory. Live GitHub evidence remains a separate evidence source and is not falsely labeled as historical RAG.

## 6. Qwen structured-output hardening

Local Qwen3 can emit reasoning wrappers such as `<think>...</think>` before the final answer. The workspace planner now strips that transport reasoning and validates only the final JSON object. Local Qwen3 requests also use `/no_think` in the evidence message to improve deterministic structured output.

Even a successful model response is only a proposal. The exact file path and search preimage are revalidated before a patch can be reviewed or written.

## 7. Built-in breadth proof

`/prototype` now registers multiple genuinely broken targets rather than a single authentication example:

1. **Broken Bearer Authentication API** — HTTP authentication contract regression.
2. **Broken Cart Total** — business-logic arithmetic regression.
3. **Broken Pagination Boundary** — off-by-one slicing regression.

Each has its own real source, tests and reset baseline. The same sequence applies:

```text
Reset
→ Scan + reproduce
→ real pytest FAIL
→ grounded diagnosis
→ Preview exact no-write patch
→ Apply exact reviewed patch
→ same pytest rerun
→ PASS = FIXED / FAIL = rollback
```

These built-in targets retain a deterministic safe-rule fallback so a hackathon network/model outage cannot destroy the core verification demonstration.

## 8. What to say to judges

Recommended:

> “Give us your bug report and the relevant files. We isolate them, retrieve relevant engineering knowledge, prove whether the local Qwen model is actually callable, show you its exact bounded patch before any write, and verify the result. If you trust the attached Python tests, the same failing tests must pass before we say VERIFIED FIXED. Without that functional proof, we only claim static validation.”

Do not say:

- that arbitrary uploaded code is always safe to execute;
- that static validation proves functional recovery;
- that Qwen ran when the model probe or proposal says otherwise;
- that the product solves every arbitrary defect;
- that the model has unrestricted access to the laptop.

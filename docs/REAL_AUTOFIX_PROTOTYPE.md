# Real AutoFix Prototype — IIT Bombay judge flow

This is the primary proof that the product can repair real local source code instead of only simulating recommendations.

## Product claim

A developer grants the platform one workspace. The platform can inventory readable source files, run a predefined validator, correlate the failure with source/test evidence, prepare a bounded edit, modify the real file, rerun the same validator, and either prove the repair or restore the original file.

The model never receives unrestricted shell authority and never receives unrestricted operating-system file access.

## Zero-cost AI strategy

The prototype does not require a paid API.

Priority order:

1. **Local Ollama** — default `qwen3:4b`, fully local, no per-call cost.
2. **Gemini Developer API free tier** — optional fallback only when `GEMINI_API_KEY` is configured locally.
3. **Deterministic evidence engine** — always available; scan/repair/verification does not depend on an external model.

Default `.env` behavior is `LLM_PROVIDER=auto`.

### Recommended hackathon laptop setup

Install Ollama before the event, then run:

```powershell
ollama pull qwen3:4b
ollama run qwen3:4b
```

The application uses Ollama's OpenAI-compatible localhost endpoint at `http://localhost:11434/v1`.

For a lighter machine you may set `OLLAMA_MODEL` to a smaller installed model. Gemma-family models can also be used through the same local OpenAI-compatible endpoint.

Gemini is optional. If you choose to use its free tier, create the key in Google AI Studio and put it only in your local `.env`:

```text
GEMINI_API_KEY=...
LLM_PROVIDER=auto
```

Never commit the key.

## Real demo target

Included target:

```text
demo_targets/broken_auth_api/
```

It is a genuine FastAPI application with a reproducible regression.

Client contract:

```text
Authorization: Bearer demo-valid-token
```

Broken source behavior:

```python
if scheme.lower() != "token":
    raise HTTPException(status_code=401, detail="Unsupported authorization scheme")
```

The parser therefore rejects the standard `Bearer` scheme and a real pytest fails.

## Before-demo preparation

From the repository root:

```powershell
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Open the frontend URL printed by `start.bat`, then open:

```text
/prototype
```

Click **Reset broken target** before presenting. This restores the checked-in broken baseline and reruns the real target tests. Reset also invalidates any previously armed repair preview.

## 60–90 second judge demonstration

### Step 1 — show the actual target

Point to the target card:

- workspace: `demo_targets/broken_auth_api`
- symptom: valid Bearer authentication returns HTTP 401
- proof: target's own pytest suite

Recommended line:

> “This folder is an independent broken application. We are not feeding the UI a fake error string.”

### Step 2 — Scan + reproduce

Click **1. Scan + reproduce**.

The backend executes only the platform-approved validator:

```text
python -m pytest -q
```

The UI must show:

```text
BEFORE: FAIL
exit code != 0
```

and the real pytest failure output.

### Step 3 — grounded diagnosis

The scanner reads `test_app.py` and `app.py` inside the selected workspace.

It observes:

```text
Test contract: Authorization: Bearer ...
Source parser: scheme.lower() != "token"
```

It therefore identifies `app.py` and the exact mismatch instead of inventing a generic auth explanation.

### Step 4 — preview and arm the exact patch

Click **2. Preview exact fix**.

The UI displays the unified diff before any write:

```diff
-    if scheme.lower() != "token":
+    if scheme.lower() != "bearer":
```

That preview is also the approval boundary. The backend stores the exact no-write `WorkspaceFixProposal` that was returned to the operator. A later Apply is allowed to consume that reviewed proposal once; it does not silently regenerate a different AI or deterministic candidate at write time.

### Step 5 — real Auto Fix

Click **3. Auto Fix + Verify**.

The backend:

1. requires a previously previewed proposal; direct Apply without one returns a conflict instead of writing;
2. consumes the exact reviewed proposal once;
3. rechecks workspace containment and the currently diagnosed target file;
4. requires the source file to still byte-match the reviewed `before` state;
5. writes only the reviewed `after` state;
6. reruns the exact same pytest command;
7. reports `FIXED` only when pytest exits `0`;
8. restores the original source automatically if verification fails;
9. does **not** substitute another candidate after a failed reviewed repair — the operator must preview again.

If anyone changes the file between Preview and Apply, the write fails closed as stale. Reset also clears the armed preview, so an old approval cannot be reused after restoring the demo target.

The judge-facing proof should end as:

```text
BEFORE  FAIL  →  AFTER  PASS
```

with the post-fix pytest output visible.

Recommended line:

> “The model may suggest the edit, but the human-approved diff is the only write authority, and tests decide whether the machine is allowed to call it fixed.”

## Why this is not a simulation

Every important artifact exists outside the presentation UI:

- real target source file;
- real target tests;
- actual subprocess exit code;
- actual pytest stdout/stderr;
- actual source-file write;
- actual unified diff;
- exact preview-to-write binding;
- actual post-edit rerun;
- actual rollback if the rerun fails.

A judge can open `demo_targets/broken_auth_api/app.py`, run the tests manually, or inspect the file after AutoFix.

## Workspace safety model

The product intentionally does **not** grant a model unrestricted whole-computer access.

Current boundaries:

- one configured workspace root;
- registered target directories only;
- path traversal rejected;
- symlinked files skipped;
- `.git`, `.ssh`, `.aws`, `.azure`, `.config`, virtual environments, caches and `node_modules` excluded;
- source files above the bounded read size skipped;
- no shell command emitted by a model is executed;
- validators are hard-coded platform capabilities, not free-form model text;
- a file write requires a preceding exact proposal preview;
- the reviewed proposal is consumed once and Reset invalidates it;
- stale source state aborts the edit;
- failed verification causes rollback;
- a failed reviewed patch cannot silently trigger an unreviewed substitute patch through the API write path.

For this single-process hackathon MVP, the armed reviewed proposal is held in process. A horizontally scaled production service should move that approval object and its one-time-consume semantics to a shared transactional store while preserving the same exact-proposal boundary.

## If Ollama is unavailable during judging

Do not panic and do not call the demo fake.

`/prototype` still performs the real failure → reviewed file edit → test verification loop through deterministic source/test evidence. The AI runtime card will truthfully show fallback state.

If a Gemini free-tier key is configured and available, the general RCA system can use it as the secondary synthesis provider.

## Reset after the demo

Click **Reset broken target**. The platform invalidates any armed preview, restores `baseline/app.py.txt` into `app.py` and proves that the target is broken again.

This makes the complete judge sequence repeatable without manually editing files between presentations.

## Final pitch

> “Most coding agents stop at generating code. Our product owns the engineering control loop: reproduce the bug, ground the diagnosis in the project, bind writes to the exact human-reviewed patch, modify only the granted workspace, rerun trusted validation, roll back on failure, and create reusable incident knowledge only after proof.”

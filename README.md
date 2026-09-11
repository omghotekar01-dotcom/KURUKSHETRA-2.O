# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It can reproduce a real local regression, retrieve relevant engineering knowledge, ground reasoning in source/tests and live repository evidence, prepare an exact bounded patch, require review before writes, rerun trusted validation, roll back failed repairs, and carry verified remediation evidence into an auditable Draft-PR workflow.

The product never auto-merges and does not expose an in-product merge or production deployment action. Merge remains an external human repository action after review.

> **Hackathon development note:** the active implementation is on `agent-build-core`. `main` remains intentionally untouched until final submission promotion is explicitly approved.

## Fastest Windows start

Requirements:

- Python **3.11.x**
- Node.js **22–24**
- npm **10–11**
- Git
- Optional but strongly recommended for the live AI demo: **Ollama + `qwen3:4b`**
- GitHub CLI (`gh`) for authenticated live remediation write/validation workflows

From the repository root:

```bat
verify.bat
setup-local-ai.bat
start.bat
```

`setup-local-ai.bat` starts/reaches Ollama, pulls `qwen3:4b`, confirms the model is installed and performs a real local inference warm-up before it reports success. If Ollama is unavailable, the built-in deterministic proof targets still work; arbitrary judge-supplied repair fails closed rather than pretending a model ran.

The launcher checks the toolchain, bootstraps dependencies, selects free local ports, injects the real backend URL into Vite, waits for backend/frontend health, prints the detected AI runtime, prints exact live URLs and opens the AI Workspace. Use the URLs printed by `start.bat`; do not assume default ports are free.

Stop launcher-managed services with:

```bat
stop.bat
```

## Unix/macOS

```bash
bash scripts/verify.sh
bash scripts/start.sh
```

Run a local Ollama service with `qwen3:4b` separately if you want the generic judge-supplied AI repair path on Unix/macOS.

## Product surfaces

- **AI Workspace** — `/` or `/workspace` — conversational engineering entry point for a bug description, GitHub repository, drag/drop source/test files, RAG context and truthful integration status
- **Test Lab** — `/test` — one judge-friendly launcher for repository incidents, uploaded files/tests, controlled broken projects/compilations and the full governed PR flow
- Incident Command — `/incidents` — persisted incident lifecycle, routing, evidence, RCA, approval and audit timeline
- **Real AutoFix** — `/prototype` — guaranteed real broken-project FAIL → reviewed repair → same-validator PASS proof
- **Judge Intake** — `/intake` — dedicated judge-supplied bug/source/test workflow with isolated RAG + grounded model repair
- AI Reasoning Lab — `/ai`
- Judge Mode — `/demo`
- Engineering Evidence Lab — `/evidence`
- Remediation Studio — `/remediate`
- Evaluation Lab — `/evaluation`
- System Readiness — `/readiness`
- FastAPI health — backend `/health`
- FastAPI docs — backend `/docs`

The specialist pages are intentionally preserved. The AI Workspace is the simple product entry point; Test Lab helps a user choose the right proof path; the specialist pages expose the engineering evidence and control boundaries a technical judge may want to inspect directly.

## Product UI system

The judge-facing application uses one white + purple visual system across all primary surfaces:

- Apple-like system typography and restrained spacing;
- compact conversational composer instead of an oversized chat box;
- visible drag/drop affordance for bounded source/test files;
- collapsible desktop navigation with persistent state and a mobile drawer;
- solid code/diff/terminal surfaces for readability;
- purple glass only for navigation/control surfaces where it helps hierarchy;
- truthful shimmer/skeleton states for model, repository, CI and validation work;
- reduced-motion and reduced-transparency accessibility fallbacks;
- denser Incident Command and Judge Demo layouts to avoid empty vertical space.

## AI Workspace

The home page is an engineering-specific conversational composer rather than a generic dashboard.

Users can:

- describe the observed bug and expected behavior in natural language;
- attach up to 12 bounded source/test files through the picker or drag/drop;
- enter the allowlisted GitHub `owner/repository` to investigate live repository evidence;
- choose production, staging or development context;
- explicitly enable trusted uploaded Python tests only when those files are safe to execute;
- test live Qwen and GitHub integration readiness;
- inspect triage, RCA, RAG and live GitHub evidence;
- review a grounded isolated-file patch and run the existing validator path.

See [`docs/AI_WORKSPACE_UX.md`](docs/AI_WORKSPACE_UX.md) for the UX and truth-boundary rationale.

## Test Lab

`/test` provides a simple decision surface for four real workflows rather than pretending every defect is the same kind of input:

1. **Repository / Incident** — investigate a live allowlisted GitHub repository.
2. **Files + Tests** — drag/drop bounded source and optional trusted tests into an isolated workspace.
3. **Project / Compilation** — use a registered broken project and deterministic validator.
4. **Full Governed Flow** — exercise evidence → approval → isolated branch → Draft PR → real CI → external human review/merge.

## Strongest hackathon proof

### 1. Guaranteed real repair proof — `/prototype`

```text
real broken target
→ real failing pytest
→ bounded source/test diagnosis
→ optional local Qwen proposal or truthful deterministic fallback
→ exact no-write preview
→ human review
→ exact file edit
→ same pytest rerun
→ PASS = FIXED
→ FAIL = rollback
```

The repository includes multiple repeatable broken targets, including authentication, cart-total arithmetic and pagination regressions.

### 2. Judge-supplied evidence — `/intake` or AI Workspace file mode

A judge/operator can type a bug report and attach up to 12 allowlisted text/code files. The backend creates an ephemeral isolated copy and never grants the model arbitrary laptop filesystem access.

```text
judge bug report + files
→ isolated temporary workspace
→ RAG over engineering runbooks
→ baseline evidence
→ real Qwen/Ollama inference when connected
→ exact bounded search/replace proposal
→ operator reviews diff
→ one-time approved write to isolated copy
→ trusted validator or static verification
→ verified fix / static-only result / rollback
```

Use **Test Qwen now** on `/intake`, **Test live integrations** in the AI Workspace, or **Test live integrations** on `/readiness` to perform a real inference probe. A model being installed/configured is not presented as proof that inference actually succeeded.

### Trusted test execution

Judge-supplied code is **not executed by default**. Without explicit trust, the intake path performs static Python/JSON validation only and labels success `STATIC_CHECK_PASSED`; it does not claim functional recovery.

If the operator explicitly enables **Trusted test execution** and supplies Python `test_*.py` files, the isolated copy runs pytest. `VERIFIED_FIXED` is allowed only when a previously failing trusted test contract passes after the exact reviewed patch.

## Broader live GitHub workflow

```text
Incident + logs + repository
→ triage / configurable owner routing
→ RAG: curated runbooks + verified resolution memory
→ live GitHub investigation
→ commits + changed files + real diff hunks
→ stack-trace/file-path correlation
→ CODEOWNERS routing/review hints when available
→ bounded source context
→ evidence-backed RCA
→ exact safety-thresholded patch proposal (NO WRITE)
→ human approve / reject
→ stale/exact-state revalidation
→ deterministic incident-fix branch
→ exact approved replacement OR safe retry reuse
→ deterministic trusted validation
→ Draft PR only if green OR reuse exact existing PR
→ live GitHub CI/check verification
→ derived verification evidence
→ external human PR review / merge under repository controls
→ runtime/human verification
→ resolved / escalated
→ verified-resolution memory
```

### Merge boundary

The product deliberately stops at a validated **Draft PR**. CI PASS records strong evidence for the remediation commit, but it does not grant merge authority. Final PR review and merge happen externally under normal GitHub/repository controls, and runtime/human verification is still required before the original incident can be considered recovered.

## Live GitHub configuration

```env
DEMO_MODE=false
GITHUB_REPOSITORY=omghotekar01-dotcom/KURUKSHETRA-2.O
GITHUB_ALLOWED_REPOSITORIES=omghotekar01-dotcom/KURUKSHETRA-2.O
ALLOW_GH_CLI_AUTH=true
GITHUB_TOKEN=
TRIAGE_OWNER_MAP=
PATCH_PROPOSAL_MIN_CORRELATION=0.18
LLM_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:4b
```

For authenticated live write actions, authenticate locally with GitHub CLI:

```powershell
gh auth status
gh auth login
```

A local environment token remains an optional alternative. Never paste tokens into issues, prompts, screenshots, repository files or chat messages.

`/readiness` performs a read-only GitHub permission probe and reports whether the configured credential actually has push permission for the allowlisted repository. The probe does **not** create a branch, commit or PR and never returns the credential value.

## RAG and model boundary

RAG is not the authority layer. Curated runbooks and previously verified resolution memory provide retrieval context; live GitHub evidence is treated separately. Local Qwen/Gemini may synthesize a bounded candidate, but the model cannot decide whether tests passed, bypass approval, choose arbitrary shell commands, access unrestricted OS paths, merge, deploy or declare production recovery.

**The model can reason and propose; evidence, validators and explicit human authority hold control.**

### Ollama/Qwen compatibility

The local runtime supports both common Ollama interfaces:

- OpenAI-compatible `/v1/models` + `/v1/chat/completions`;
- native `/api/tags` + `/api/chat` fallback.

This prevents a working local Qwen installation from being reported unavailable merely because one compatibility route differs across Ollama versions.

## Reproducibility

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- exact direct backend/frontend package versions
- committed npm lockfile v3
- bootstrap/remediation frontend validation uses `npm ci`
- Windows dependency-lock recovery handles project-owned Vite/Rolldown file locks
- GitHub Actions includes Linux backend/frontend jobs and a real Windows clean-checkout bootstrap/acceptance job
- release contract asserts the AI Workspace, Test Lab, judge-intake, model-probe, AutoFix, UI loading system and core security surfaces remain present

## Security and truth boundaries

- Investigation is read-only until explicit approval.
- Patch proposal generation performs no write.
- Every patch write is tied to one exact reviewed proposal.
- Stale/conflicting state fails closed.
- Judge uploads are copied into an isolated temporary workspace.
- Path traversal, absolute paths and sensitive/build directories are blocked from judge intake.
- Arbitrary uploaded code is not executed unless trusted-test execution is explicitly enabled.
- Failed repair validation restores the original isolated file.
- Weak or absent generic model evidence produces no arbitrary patch.
- No in-product merge or production deployment action exists.
- CI failure can derive failed incident-verification evidence.
- CI PASS never auto-resolves an incident; runtime/human verification remains required.
- Recognized credential patterns are redacted from incident and repository evidence surfaces.
- Repository/uploaded text is treated as untrusted evidence, not executable instructions.
- Correlation is investigation guidance, not causal proof.
- `STATIC_CHECK_PASSED` is never described as functional recovery.
- A `live` model label is backed by an actual inference probe rather than installation/configuration alone.

## Verification record

See [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) for the latest exact tested head, backend test count, frontend build result and Windows clean-clone acceptance result. Do not infer a release claim from an older commit number in this README.

## Project documentation

- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — current capability/status ledger
- [`docs/AI_WORKSPACE_UX.md`](docs/AI_WORKSPACE_UX.md) — product UX, loading, live-state and connector direction
- [`docs/JUDGE_SUPPLIED_INTAKE.md`](docs/JUDGE_SUPPLIED_INTAKE.md) — arbitrary judge bug/file workflow and safety model
- [`docs/REAL_AUTOFIX_PROTOTYPE.md`](docs/REAL_AUTOFIX_PROTOTYPE.md) — repeatable real local repair proof
- [`docs/IIT_BOMBAY_FINAL_DEMO.md`](docs/IIT_BOMBAY_FINAL_DEMO.md) — final judge-facing demo sequence
- [`docs/REAL_USE_AUDIT.md`](docs/REAL_USE_AUDIT.md) — realistic usefulness audit
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — security/readiness hardening
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — presentation/recovery sequence
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](docs/RELEASE_CANDIDATE_FREEZE.md) — release boundary

## Originality and open-source use

This repository is not registered as a fork or template-derived repository. The project uses standard open-source frameworks/libraries including React, TypeScript, Vite, FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Lucide React and SQLite. AI-assisted development tools were used as development support; project-specific workflow integration and final implementation are reviewed and tested in this repository.

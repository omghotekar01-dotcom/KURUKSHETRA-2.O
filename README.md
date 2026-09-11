# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It can reproduce a real local regression, retrieve relevant engineering knowledge, ground reasoning in source/tests and live repository evidence, prepare an exact bounded patch, require review before writes, rerun trusted validation, roll back failed repairs, and carry verified remediation evidence into an auditable workflow.

The system never auto-merges or deploys production code.

> **Hackathon development note:** the active implementation is on `agent-build-core`. `main` remains intentionally untouched until final submission promotion is explicitly approved.

## Fastest Windows start

Requirements:

- Python **3.11.x**
- Node.js **22–24**
- npm **10–11**
- Git
- Optional but strongly recommended for the live AI demo: **Ollama + `qwen3:4b`**
- GitHub CLI (`gh`) only for authenticated live remediation write/validation workflows

From the repository root:

```bat
verify.bat
setup-local-ai.bat
start.bat
```

`setup-local-ai.bat` starts/reaches Ollama, pulls `qwen3:4b`, verifies that the model is installed, and prepares the zero-cost local model path. If Ollama is unavailable, the built-in deterministic proof targets still work; arbitrary judge-supplied repair fails closed rather than pretending a model ran.

The launcher checks the toolchain, bootstraps dependencies, selects free local ports, injects the real backend URL into Vite, waits for backend/frontend health, prints the detected AI runtime, prints exact live URLs and opens the dashboard. Use the URLs printed by `start.bat`; do not assume default ports are free.

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

- Incident Command Dashboard — `/`
- **Real AutoFix** — `/prototype` — guaranteed real broken-project FAIL → reviewed repair → same-validator PASS proof
- **Judge Intake** — `/intake` — judge types a bug report and attaches source/test files for isolated RAG + grounded model repair
- AI Reasoning Lab — `/ai`
- Judge Mode — `/demo`
- Engineering Evidence Lab — `/evidence`
- Remediation Studio — `/remediate`
- Evaluation Lab — `/evaluation`
- System Readiness — `/readiness`
- FastAPI health — backend `/health`
- FastAPI docs — backend `/docs`

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

### 2. Judge-supplied evidence — `/intake`

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

Use **Test Qwen now** on `/intake` to perform a real chat-completions inference probe. The page shows the actual provider, model, latency and result. Configuration alone is not presented as proof that Qwen ran.

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
→ human runtime verification
→ resolved / escalated
→ verified-resolution memory
```

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

For authenticated live write actions, authenticate locally with GitHub CLI (`gh auth login`) or provide a suitable token through the local environment. Never paste tokens into issues, prompts, screenshots, repository files or chat messages.

## RAG and model boundary

RAG is not the authority layer. Curated runbooks and previously verified resolution memory provide retrieval context; live GitHub evidence is treated separately. Local Qwen/Gemini may synthesize a bounded candidate, but the model cannot decide whether tests passed, bypass approval, choose arbitrary shell commands, access unrestricted OS paths, merge, deploy or declare production recovery.

**The model can reason and propose; evidence and validators hold authority.**

## Reproducibility

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- exact direct backend/frontend package versions
- committed npm lockfile v3
- bootstrap/remediation frontend validation uses `npm ci`
- Windows dependency-lock recovery handles project-owned Vite/Rolldown file locks
- GitHub Actions includes Linux backend/frontend jobs and a real Windows clean-checkout bootstrap/acceptance job
- release contract asserts the judge-intake, model-probe, AutoFix and safety surfaces remain present

## Security and truth boundaries

- Investigation is read-only until explicit approval.
- Patch proposal generation performs no write.
- Every write is tied to one exact reviewed proposal.
- Stale/conflicting state fails closed.
- Judge uploads are copied into an isolated temporary workspace.
- Path traversal, absolute paths and sensitive/build directories are blocked from judge intake.
- Arbitrary uploaded code is not executed unless trusted-test execution is explicitly enabled.
- Failed repair validation restores the original isolated file.
- Weak or absent generic model evidence produces no arbitrary patch.
- High-risk merge/deploy/destructive actions remain recommendation-only.
- No automatic merge or production deployment exists.
- CI failure can derive failed incident-verification evidence.
- CI PASS never auto-resolves an incident; runtime/human verification remains required.
- Recognized credential patterns are redacted from incident and repository evidence surfaces.
- Repository/uploaded text is treated as untrusted evidence, not executable instructions.
- Correlation is investigation guidance, not causal proof.

## Verification record

See [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) for the latest exact tested head, backend test count, frontend build result and Windows clean-clone acceptance result. Do not infer a release claim from an older commit number in this README.

## Project documentation

- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — current capability/status ledger
- [`docs/JUDGE_SUPPLIED_INTAKE.md`](docs/JUDGE_SUPPLIED_INTAKE.md) — arbitrary judge bug/file workflow and safety model
- [`docs/REAL_AUTOFIX_PROTOTYPE.md`](docs/REAL_AUTOFIX_PROTOTYPE.md) — repeatable real local repair proof
- [`docs/IIT_BOMBAY_FINAL_DEMO.md`](docs/IIT_BOMBAY_FINAL_DEMO.md) — final judge-facing demo sequence
- [`docs/REAL_USE_AUDIT.md`](docs/REAL_USE_AUDIT.md) — realistic usefulness audit
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — security/readiness hardening
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — presentation/recovery sequence
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](docs/RELEASE_CANDIDATE_FREEZE.md) — release boundary

## Originality and open-source use

This repository is not registered as a fork or template-derived repository. The project uses standard open-source frameworks/libraries including React, TypeScript, Vite, FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Lucide React and SQLite. AI-assisted development tools were used as development support; project-specific workflow integration and final implementation are reviewed and tested in this repository.

# KURUKSHETRA 2.0 — AI Agentic Bug Router

**Project ID: KH059**

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It accepts a bug report, source/test files or an allowlisted GitHub repository, gathers evidence, retrieves relevant engineering knowledge, builds an evidence-backed root-cause hypothesis, prepares a bounded patch, requires human approval before repository writes, validates the exact reviewed change and carries verified remediation evidence into a Draft-PR workflow.

## What the system demonstrates

- incident intake, persistence, triage and component/team routing;
- RAG over curated engineering runbooks and verified resolution memory;
- live GitHub commits, issues, changed files, diffs and bounded source context;
- suspicious-hunk ranking and evidence-backed RCA;
- judge-supplied source/test intake in an isolated temporary workspace;
- local Qwen/Ollama grounded patch proposals with deterministic fail-closed fallback;
- exact reviewable search/replace patches rather than unrestricted code generation;
- explicit APPROVE / REJECT before repository writes;
- isolated remediation branches and deterministic validation;
- Draft PR creation only after validation passes;
- real GitHub CI/check-status verification;
- measured Evaluation Lab benchmarks;
- safe-stop behavior when evidence is weak or integrations are unavailable.

## Quick start — Windows

Requirements:

- Python 3.11.x
- Node.js 22–24
- npm 10–11
- Git
- Ollama with `qwen3:4b` for the live local-model path
- GitHub CLI (`gh`) for authenticated remediation workflows

From the repository root:

```bat
verify.bat
setup-local-ai.bat
start.bat
```

Stop launcher-managed services with:

```bat
stop.bat
```

The launcher performs environment checks, bootstraps dependencies, selects available local ports, waits for backend/frontend health and prints the exact product URLs. Use the URLs printed by the launcher rather than assuming fixed ports.

## Unix / macOS

```bash
bash scripts/verify.sh
bash scripts/start.sh
```

Run Ollama separately if you want the generic judge-supplied local-model repair path.

## Product surfaces

| Surface | Route | Purpose |
|---|---|---|
| AI Workspace | `/` or `/workspace` | Main conversational engineering entry point for bug text, repository context and files |
| Test Lab | `/test` | Chooses the correct proof path: repository, files/tests, controlled project or governed PR flow |
| Incident Command | `/incidents` | Persisted incident lifecycle, routing, evidence, RCA and timeline |
| Real AutoFix | `/prototype` | Controlled real FAIL → reviewed repair → same-validator PASS proof |
| Judge Intake | `/intake` | Judge-supplied bug/source/test workflow with isolated RAG + grounded repair |
| AI Reasoning Lab | `/ai` | Triage → RAG → repository evidence → RCA → policy reasoning trace |
| Judge Mode | `/demo` | Guided golden flow for presentation |
| Engineering Evidence Lab | `/evidence` | Live commits, diff hunks, source context and investigation evidence |
| Remediation Studio | `/remediate` | Exact patch review, approval, isolated branch, validation, Draft PR and CI |
| Evaluation Lab | `/evaluation` | Repeatable measured benchmark scorecard |
| System Readiness | `/readiness` | Active model/GitHub integration probes and safety status |

## Core workflow

```text
bug report / logs / files / repository
→ incident intake
→ triage + routing
→ RAG context
→ live repository evidence when available
→ evidence-backed RCA + next diagnostic
→ bounded exact patch proposal (NO WRITE)
→ human APPROVE / REJECT
→ stale/exact-state revalidation
→ isolated fix branch or isolated intake copy
→ exact reviewed replacement only
→ deterministic trusted validation
→ Draft PR only if green
→ real GitHub CI/check evidence
→ external human repository review/merge
→ runtime/human verification
```

## Judge-supplied files and trusted tests

Uploaded files are copied into an isolated temporary workspace. The model receives only bounded uploaded text and cannot access arbitrary laptop paths.

Without explicit trust, intake uses static validation only and may return `STATIC_CHECK_PASSED`. It does not claim functional recovery.

If **Trusted test execution** is enabled and Python `test_*.py` files are supplied, the same trusted pytest contract is run before and after the exact reviewed patch. `VERIFIED_FIXED` is allowed only for a real failing baseline followed by a passing post-patch run.

## Live local model

The default zero-cost model path is:

```text
Ollama localhost
→ qwen3:4b
→ optional configured Gemini fallback
→ deterministic fallback only where an explicit safe rule exists
```

`setup-local-ai.bat` checks Ollama, installs the configured model when needed and performs a real native `/api/chat` warm-up before reporting inference readiness.

The runtime supports both Ollama interfaces:

- native `/api/tags` + `/api/chat`;
- OpenAI-compatible `/v1/models` + `/v1/chat/completions`.

Generic Judge Intake fails closed when a valid grounded model candidate cannot be produced; it does not invent an arbitrary patch.

## GitHub remediation boundary

Investigation is read-only until a human approves the exact proposal. Approval may create a real `incident-fix/...` branch, apply only the reviewed replacement, run predefined validation and create a Draft PR when validation is green.

The product never auto-merges and never deploys production. CI PASS is evidence for the remediation commit, not proof that production recovered. Final repository merge and runtime verification remain human decisions.

## Configuration

Create `.env` from `.env.example` and keep credentials local.

Typical local settings:

```env
DEMO_MODE=false
GITHUB_REPOSITORY=omghotekar01-dotcom/KURUKSHETRA-2.O
GITHUB_ALLOWED_REPOSITORIES=omghotekar01-dotcom/KURUKSHETRA-2.O
ALLOW_GH_CLI_AUTH=true
GITHUB_TOKEN=
LLM_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:4b
PATCH_PROPOSAL_MIN_CORRELATION=0.18
```

For GitHub CLI authentication:

```powershell
gh auth status
gh auth login
```

Never commit or paste tokens into repository files, screenshots or issue text.

## Security and truth boundaries

- repository investigation is read-only until explicit approval;
- every write is bound to one exact reviewed proposal;
- stale or conflicting source state fails closed;
- uploaded files remain inside an isolated temporary workspace;
- traversal, absolute paths and sensitive/build directories are blocked;
- arbitrary uploaded code is not executed unless trusted-test execution is explicitly enabled;
- failed repair validation restores the original isolated source;
- recognized credential patterns are redacted from normal evidence surfaces;
- repository/log/upload text is treated as untrusted evidence, not executable instruction;
- correlation ranks investigation targets but is never presented as causal proof;
- `STATIC_CHECK_PASSED` is not described as functional recovery;
- model labels are backed by active inference probes rather than configuration alone;
- missing, unknown, pending or failed CI checks are never promoted to PASS;
- no unrestricted shell, filesystem, merge or production-deploy authority is given to the model.

## Technology stack

**Frontend:** React, TypeScript, Vite, Lucide React  
**Backend:** FastAPI, Pydantic, Uvicorn, HTTPX, SQLite  
**Testing:** Pytest + GitHub Actions  
**Local AI:** Ollama + Qwen3  
**Repository integration:** GitHub REST/CLI workflows

The project uses standard open-source dependencies through their normal package ecosystems. See the package manifests and lockfiles for exact versions.

## Reproducibility

- `.python-version` defines the Python target;
- `.nvmrc` defines the Node target;
- direct backend/frontend dependencies are pinned;
- `frontend/package-lock.json` is committed;
- frontend bootstrap uses `npm ci`;
- GitHub Actions validates backend, frontend and a Windows clean-checkout path;
- `verify.bat` and `scripts/verify.sh` provide local release checks.

## Documentation

- [`docs/AI_WORKSPACE_UX.md`](docs/AI_WORKSPACE_UX.md) — workspace UX and live-state behavior
- [`docs/JUDGE_SUPPLIED_INTAKE.md`](docs/JUDGE_SUPPLIED_INTAKE.md) — file/test intake and safety model
- [`docs/REAL_AUTOFIX_PROTOTYPE.md`](docs/REAL_AUTOFIX_PROTOTYPE.md) — repeatable local repair proof
- [`docs/EVALUATION_LAB.md`](docs/EVALUATION_LAB.md) — benchmark design and interpretation
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — presentation and recovery sequence
- [`docs/PATCH_REMEDIATION_MILESTONE.md`](docs/PATCH_REMEDIATION_MILESTONE.md) — repository remediation contract
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — security/readiness hardening
- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — release status and verified capability summary

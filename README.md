# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It accepts a software incident, routes it to the likely technical owner, searches previous verified knowledge, investigates the attached GitHub repository, ranks relevant commits and diff hunks, prepares an exact patch proposal, requires human approval before any write, validates the approved change on an isolated branch, and creates a Draft Pull Request only after the configured checks pass.

The system never auto-merges or deploys production code.

> **Hackathon development note:** the active implementation is on `agent-build-core`. `main` remains intentionally untouched until final submission promotion is explicitly approved.

## Fastest Windows start

Requirements:

- Python **3.11.x**
- Node.js **22–24**
- npm **10–11**
- Git
- GitHub CLI (`gh`) only for authenticated live remediation write/validation workflows

From the repository root:

```bat
verify.bat
start.bat
```

The launcher checks the toolchain, bootstraps dependencies, selects free local ports, injects the real backend URL into Vite, waits for backend/frontend health, prints exact live URLs and opens the dashboard. Use the URLs printed by `start.bat`; do not assume default ports are free.

Stop launcher-managed services with:

```bat
stop.bat
```

## Unix/macOS

```bash
bash scripts/verify.sh
bash scripts/start.sh
```

## Product surfaces

- Incident Command Dashboard — `/`
- Judge Mode — `/demo`
- Engineering Evidence Lab — `/evidence`
- Remediation Studio — `/remediate`
- Evaluation Lab — `/evaluation`
- System Readiness — `/readiness`
- FastAPI health — backend `/health`
- FastAPI docs — backend `/docs`

## Actual supported workflow

```text
Incident + logs + repository
→ triage / configurable owner routing
→ historical evidence
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
```

Example real-team mapping:

```env
TRIAGE_OWNER_MAP=Authentication=identity-platform,Database=data-reliability,Backend=api-platform,Frontend=web-experience,Infrastructure=sre
```

For authenticated live write actions, authenticate locally with GitHub CLI (`gh auth login`) or provide a suitable token through the local environment. Never paste tokens into issues, prompts, screenshots, repository files or chat messages.

## Reproducibility

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- exact top-level backend versions
- exact direct frontend/tooling versions
- committed npm lockfile v3
- bootstrap/remediation frontend validation uses `npm ci`
- GitHub Actions includes Linux backend/frontend jobs and a real Windows clean-checkout bootstrap/acceptance job

## Security and truth boundaries

- Investigation is read-only until explicit approval.
- Patch proposal generation performs no write.
- Weakly correlated patch candidates are blocked.
- Every repository write is tied to one exact approved proposal.
- Duplicate approvals reuse exact successful remediation state.
- Stale/conflicting state fails closed.
- Unsupported executable/configuration types fail closed without a trusted validator.
- High-risk merge/deploy/destructive actions remain recommendation-only.
- No automatic merge or production deployment exists.
- CI failure can derive failed incident-verification evidence.
- CI PASS never auto-resolves the incident; runtime/human verification remains required.
- Recognized credential patterns are redacted from incident and repository evidence surfaces.
- Repository text is treated as untrusted evidence, not executable instructions.
- Correlation is investigation guidance, not causal proof.

## Latest verified executable build

GitHub Actions **run #409** / run ID `34597412643` on executable code head `18112b436803f747a23d60bf5ce73c952f9523a7` passed:

```text
Backend compile:                      PASS
Backend tests:                        73 passed, 0 failures
Frontend locked install/build:        PASS
Windows launcher syntax:              PASS
Windows environment preflight:        PASS
Windows clean bootstrap:              PASS
Release candidate contract:           PASS
Clean-clone acceptance:               4/4 PASS
Release-candidate acceptance:         PASS
```

Subsequent closure commits are documentation-only.

## Project documentation

- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — capability/status ledger
- [`docs/REAL_USE_AUDIT.md`](docs/REAL_USE_AUDIT.md) — realistic usefulness audit
- [`docs/REPRODUCIBLE_STARTUP_MILESTONE.md`](docs/REPRODUCIBLE_STARTUP_MILESTONE.md) — reproducible setup proof
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — security/readiness hardening
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — presentation/recovery sequence
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](docs/RELEASE_CANDIDATE_FREEZE.md) — final release boundary

## Originality and open-source use

This repository is not registered as a fork or template-derived repository. The project uses standard open-source frameworks/libraries including React, TypeScript, Vite, FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Lucide React and SQLite. AI-assisted development tools were used as development support; project-specific workflow integration and final implementation are reviewed and tested in this repository.

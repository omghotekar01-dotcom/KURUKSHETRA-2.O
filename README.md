# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It accepts a software incident, routes it to the likely technical owner, searches previous verified knowledge, investigates the attached GitHub repository, ranks relevant commits and diff hunks, prepares an exact patch proposal, requires human approval before any write, validates the approved change on an isolated branch, and creates a Draft Pull Request only after the configured checks pass.

The system never auto-merges or deploys production code.

> **Hackathon development note:** the active implementation is on `agent-build-core` until the final release-candidate freeze. `main` remains intentionally untouched during active integration.

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

On launch the project:

1. checks the local toolchain,
2. creates `.env` from `.env.example` if needed,
3. creates `backend/.venv`,
4. installs pinned Python dependencies and the locked npm dependency tree,
5. selects a free backend port (prefers `8000`, falls back from `8011`),
6. selects a free frontend port (prefers `5173`, falls back from `5181`),
7. injects the selected backend URL into Vite,
8. waits for backend `/health` and frontend HTTP,
9. prints the exact live URLs and opens the dashboard.

**Use the URLs printed by `start.bat`; do not assume the default ports are free.**

Stop launcher-managed services with:

```bat
stop.bat
```

## Unix/macOS

```bash
bash scripts/verify.sh
bash scripts/start.sh
```

Stop:

```bash
bash scripts/stop.sh
```

## Product surfaces

The launcher prints the exact selected port for every surface:

- Incident Command Dashboard — `/`
- Judge Mode — `/demo`
- Engineering Evidence Lab — `/evidence`
- Remediation Studio — `/remediate`
- Evaluation Lab — `/evaluation`
- System Readiness — `/readiness`
- FastAPI health — backend `/health`
- FastAPI docs — backend `/docs`

## Current live workflow

```text
Incident + logs + repository
→ triage / route
→ historical evidence
→ live GitHub investigation
→ recent commits + changed files + real diff hunks
→ stack-trace/file-path correlation
→ CODEOWNERS routing/review hints when available
→ bounded source context
→ evidence-backed RCA
→ exact safety-gated patch proposal (NO WRITE)
→ human approve / reject
→ stale-proposal + exact-file revalidation
→ deterministic incident-fix branch
→ exact approved replacement OR safe retry reuse
→ deterministic validation gate
→ Draft PR only if green OR reuse exact existing PR
→ live GitHub CI/check verification
→ derived verification evidence
→ human runtime verification
→ resolved / escalated
→ verified-resolution memory
```

Parallel trust surfaces:

```text
Evaluation Lab → measured deterministic benchmark cases
System Readiness → runtime mode + configuration + safety boundary
```

## Live GitHub configuration

The normal product path is live-first. `DEMO_MODE=false` by default.

Copy/edit `.env` locally only; never commit it. Important fields:

```env
DEMO_MODE=false
GITHUB_REPOSITORY=omghotekar01-dotcom/KURUKSHETRA-2.O
GITHUB_ALLOWED_REPOSITORIES=omghotekar01-dotcom/KURUKSHETRA-2.O
ALLOW_GH_CLI_AUTH=true
GITHUB_TOKEN=
TRIAGE_OWNER_MAP=
PATCH_PROPOSAL_MIN_CORRELATION=0.18
```

`TRIAGE_OWNER_MAP` can map components to real organization teams without changing code, for example:

```env
TRIAGE_OWNER_MAP=Authentication=identity-platform,Database=data-reliability,Backend=api-platform,Frontend=web-experience,Infrastructure=sre
```

For authenticated live write actions, either authenticate GitHub CLI:

```bash
gh auth login
gh auth status
```

or provide a suitable token through the local environment. Never paste tokens into issues, prompts, screenshots, repository files or chat messages.

## Reproducibility

The tested local toolchain is recorded in:

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- `backend/requirements.txt` → exact top-level backend versions
- `frontend/package.json` → exact direct frontend/tooling versions
- `frontend/package-lock.json` → npm lockfile v3 with transitive tree + integrity hashes

Bootstrap uses `npm ci`. GitHub Actions runs Linux backend/frontend jobs and a real `windows-latest` clean-checkout bootstrap/acceptance job.

## Security and trust boundaries

- Repository investigation is read-only until explicit approval.
- Patch proposal generation performs no repository write.
- Weakly correlated patch candidates are blocked by the configured safety threshold.
- Every repository write is tied to one exact human-approved proposal.
- Duplicate approvals reuse exact successful remediation state instead of creating duplicate branches/PRs.
- Stale or conflicting state fails closed.
- Unsupported executable/configuration file types fail closed when no trusted deterministic validator exists.
- High-risk merge/deploy/destructive actions remain recommendation-only.
- Passing CI never triggers automatic merge or claims production recovery.
- CI failure can derive failed incident-verification evidence; CI PASS still requires runtime/human verification.
- Incident text/logs redact recognized credential patterns before normal persistence/display.
- Commit messages, issue titles/labels, diff lines and bounded source snippets redact recognized credential patterns before UI exposure.
- Repository text is treated as **untrusted evidence, not executable instructions**.
- Prompt-like instruction markers in repository evidence are surfaced as untrusted-data warnings.
- Readiness reports whether credentials are configured but never returns their values.

These deterministic safeguards are defense-in-depth; they are not a claim of complete DLP or universal prompt-injection protection.

## Latest verified build

GitHub Actions run **#409** on executable code head `18112b436803f747a23d60bf5ce73c952f9523a7` passed:

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

The later documentation updates do not change that validated executable behavior.

## Development / submission links

Current working-code branch:

`https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O/tree/agent-build-core`

Repository root (use after final release is promoted to `main`):

`https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O`

Draft integration PR: `agent-build-core` → `develop`.

## Project documentation

- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — current verified capability/status ledger
- [`docs/REAL_USE_AUDIT.md`](docs/REAL_USE_AUDIT.md) — practical usefulness audit and realistic regression proof
- [`docs/REPRODUCIBLE_STARTUP_MILESTONE.md`](docs/REPRODUCIBLE_STARTUP_MILESTONE.md) — reproducible setup proof
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — readiness/redaction/untrusted-evidence hardening
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — safe presentation and recovery sequence
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](docs/RELEASE_CANDIDATE_FREEZE.md) — release-candidate boundary

## Originality and open-source use

This GitHub repository is not registered as a fork or template-derived repository. The project uses standard open-source frameworks/libraries such as React, TypeScript, Vite, FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Lucide React and SQLite. AI-assisted development tools were used for brainstorming, architecture discussion, implementation assistance, debugging, testing and documentation; project-specific workflow integration and final implementation are reviewed and tested in this repository.

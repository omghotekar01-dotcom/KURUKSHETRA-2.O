# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It accepts a software incident, routes it to the likely technical owner, searches previous verified knowledge, investigates the attached GitHub repository, ranks relevant commits and diff hunks, prepares an exact patch proposal, requires human approval before any write, validates the approved change on an isolated branch, and creates a Draft Pull Request only after configured checks pass.

The system never auto-merges or deploys production code.

> **Hackathon release-candidate note:** the completed implementation is frozen on `agent-build-core` until the team explicitly promotes the reviewed build for final submission. `main` remains intentionally untouched during this stage.

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

The launcher checks the local toolchain, creates `.env` from `.env.example` when absent, creates the backend virtual environment, installs pinned/locked dependencies, automatically chooses free backend/frontend ports, injects the selected backend URL into Vite, waits for both services to become healthy, and prints the exact live URLs.

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

- **Judge Mode — `/demo`**
- Incident Command Dashboard — `/`
- Engineering Evidence Lab — `/evidence`
- Remediation Studio — `/remediate`
- Evaluation Lab — `/evaluation`
- System Readiness — `/readiness`
- FastAPI health — backend `/health`
- FastAPI docs — backend `/docs`

## Judge Mode

`/demo` is the recommended hackathon presentation entrypoint. It runs a controlled golden authentication incident through readiness, incident creation, routing, historical retrieval, RCA, live GitHub evidence and exact patch-proposal generation.

Repository writes remain **locked by default**. The demo must reach an exact reviewable patch before a human can separately enable **Arm live remediation** and approve the bounded write. If evidence is stale, missing or ambiguous, Judge Mode displays an explicit fail-closed result instead of inventing a patch. If a Draft PR is created, Judge Mode can surface the real GitHub CI state.

```text
Golden incident
→ readiness
→ routing
→ historical evidence
→ RCA
→ live GitHub commits/diffs/source context
→ exact patch proposal (NO WRITE)
→ HUMAN APPROVAL BOUNDARY
→ optional isolated remediation branch
→ deterministic validation
→ Draft PR
→ real GitHub CI
```

Resetting Judge Mode clears only the presentation view; the incident audit history remains intact.

## Current live workflow

```text
Incident + logs + repository
→ triage / route
→ historical evidence
→ live GitHub investigation
→ recent commits + changed files + real diff hunks
→ bounded source context
→ evidence-backed RCA
→ exact patch proposal (NO WRITE)
→ human approve / reject
→ stale-proposal + exact-file revalidation
→ deterministic incident-fix branch
→ exact approved replacement OR safe retry reuse
→ deterministic validation gate
→ Draft PR only if green OR reuse exact existing PR
→ live GitHub CI/check verification
→ human runtime verification
→ resolved / escalated
→ verified-resolution memory
```

Parallel trust surfaces:

```text
Evaluation Lab → measured deterministic benchmark cases
System Readiness → runtime mode + configuration + safety boundary
Judge Mode → controlled end-to-end presentation flow
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
```

For authenticated live write actions, either authenticate GitHub CLI locally:

```bash
gh auth login
gh auth status
```

or provide a suitable token through the local environment. Never paste tokens into issues, prompts, screenshots, repository files or chat messages.

## Reproducibility and release gate

The tested local toolchain is recorded in:

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- `backend/requirements.txt` → exact top-level backend versions
- `frontend/package.json` → exact direct frontend/tooling versions
- `frontend/package-lock.json` → npm lockfile v3 with transitive tree + integrity hashes

Bootstrap uses `npm ci`. `scripts/acceptance.py` now requires four release-candidate checks to pass:

```text
backend compile
backend test suite
frontend production build
release candidate contract
```

The release contract verifies the critical routes/artifacts, Judge Mode's locked-by-default write boundary, explicit approval requirement, fail-closed behavior, CI hook, lockfile, launcher links, README safety statements and that `.env` is not tracked.

## Security and trust boundaries

- Repository investigation is read-only until explicit approval.
- Patch proposal generation performs no repository write.
- Every repository write is tied to one exact human-approved proposal.
- Duplicate approvals reuse exact successful remediation state instead of creating duplicate branches/PRs.
- Stale or conflicting state fails closed.
- High-risk merge/deploy/destructive actions remain recommendation-only.
- Passing CI never triggers automatic merge or claims production recovery.
- Incident text/logs redact recognized credential patterns before normal persistence/display.
- Commit messages, issue titles/labels, diff lines and bounded source snippets redact recognized credential patterns before UI exposure.
- Repository text is treated as **untrusted evidence, not executable instructions**.
- Prompt-like instruction markers in repository evidence are surfaced as untrusted-data warnings.
- Readiness reports whether credentials are configured but never returns their values.

These deterministic safeguards are defense-in-depth; they are not a claim of complete DLP or universal prompt-injection protection.

## Latest verified release-candidate build

GitHub Actions run **#358** / run ID `34595268159` on code head `b6e4959971b08adcf53fa83b9f98fd8c6aca0f6a` completed successfully:

```text
Backend compile:                       PASS
Backend tests:                         59 passed, 0 failures
Frontend locked install/build:         PASS
Windows launcher syntax:               PASS
Windows environment preflight:         PASS
Windows clean bootstrap:               PASS
Release candidate contract:            PASS
Clean-clone acceptance:                4/4 PASS
Release-candidate acceptance:          PASS
```

This is the frozen executable release-candidate proof point. Later documentation-only edits do not change that validated executable snapshot.

## Development / submission links

Current working-code branch:

`https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O/tree/agent-build-core`

Repository root (use after final release is explicitly promoted to `main`):

`https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O`

Draft integration PR: `agent-build-core` → `develop`.

## Project documentation

- [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) — verified capability/status ledger
- [`docs/RELEASE_CANDIDATE_FREEZE.md`](docs/RELEASE_CANDIDATE_FREEZE.md) — frozen release-candidate proof and final rehearsal instructions
- [`docs/REPRODUCIBLE_STARTUP_MILESTONE.md`](docs/REPRODUCIBLE_STARTUP_MILESTONE.md) — reproducible setup proof
- [`docs/SECURITY_READINESS_MILESTONE.md`](docs/SECURITY_READINESS_MILESTONE.md) — readiness/redaction/untrusted-evidence hardening
- [`docs/JUDGE_DEMO_RUNBOOK.md`](docs/JUDGE_DEMO_RUNBOOK.md) — safe presentation and recovery sequence

## Originality and open-source use

This GitHub repository is not registered as a fork or template-derived repository. The project uses standard open-source frameworks/libraries such as React, TypeScript, Vite, FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Lucide React and SQLite. AI-assisted development tools were used for brainstorming, architecture discussion, implementation assistance, debugging, testing and documentation; project-specific workflow integration and final implementation are reviewed and tested in this repository.

## Scope-completion boundary

The planned **hackathon MVP scope is complete** on the validated release-candidate snapshot above. That does not mean the software is universally bug-free or production-enterprise complete. Future work such as horizontal-scale distributed locking, fully hashed transitive Python locking, broader semantic patch synthesis, enterprise authentication/authorization and production deployment infrastructure is intentionally outside this hackathon release scope.

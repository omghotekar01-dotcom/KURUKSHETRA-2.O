# AI Agentic Bug Router

**From bug report to evidence-backed, human-approved, verified fix.**

AI Agentic Bug Router is a live-first engineering incident-response MVP. It accepts a software incident, routes it to the likely technical owner, searches previous verified knowledge, investigates the attached GitHub repository, ranks relevant commits and diff hunks, prepares an exact patch proposal, requires human approval before any write, validates the approved change on an isolated branch, and creates a Draft Pull Request only after the configured checks pass.

The system never auto-merges or deploys production code.

## Fastest Windows start

Requirements:

- Python **3.11.x**
- Node.js **22–24**
- npm **10–11**
- Git
- GitHub CLI (`gh`) only for live remediation write/validation workflows

From the repository root:

```bat
start.bat
```

On the first run the launcher:

1. checks the local toolchain,
2. creates `.env` from `.env.example` if needed,
3. creates `backend/.venv`,
4. installs the pinned Python dependencies and the locked npm dependency tree,
5. starts FastAPI on port `8000`,
6. starts Vite on port `5173`,
7. waits for the backend health endpoint,
8. opens the dashboard.

Stop the local services with:

```bat
stop.bat
```

Run the full local acceptance suite with:

```bat
verify.bat
```

## Unix/macOS

```bash
bash scripts/start.sh
```

Acceptance:

```bash
bash scripts/verify.sh
```

Stop:

```bash
bash scripts/stop.sh
```

## Product surfaces

- Dashboard — `http://127.0.0.1:5173`
- FastAPI health — `http://127.0.0.1:8000/health`
- FastAPI docs — `http://127.0.0.1:8000/docs`
- Engineering Evidence Lab — `http://127.0.0.1:5173/evidence`
- Remediation Studio — `http://127.0.0.1:5173/remediate`
- Evaluation Lab — `http://127.0.0.1:5173/evaluation`

## Current live workflow

```text
Incident + logs + repository
→ triage / route
→ historical evidence
→ live GitHub investigation
→ recent commits + changed files + real diff hunks
→ bounded source context
→ evidence-backed RCA
→ exact patch proposal (no write)
→ human approve / reject
→ stale-proposal and exact-file revalidation
→ deterministic incident-fix branch
→ apply only approved replacement
→ deterministic validation gate
→ Draft PR only if green
→ live GitHub CI/check verification
→ human runtime verification
→ resolved / escalated
→ verified-resolution memory
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

For live write actions you can either authenticate GitHub CLI:

```bash
gh auth login
gh auth status
```

or provide a suitable token through the local environment. Never paste or commit tokens into repository files.

## Reproducibility

The tested and frozen local toolchain is recorded in:

- `.python-version` → Python 3.11
- `.nvmrc` → Node 22.23.2
- `backend/requirements.txt` → exact top-level backend versions from a green CI build
- `frontend/package.json` → exact direct frontend/tooling versions
- `frontend/package-lock.json` → lockfile v3 with the complete npm dependency tree and integrity hashes

Bootstrap uses `npm ci`, so the local and CI frontend install must match the committed lockfile instead of resolving a new dependency tree.

GitHub Actions also performs a clean-checkout Windows acceptance run in addition to the Linux backend/frontend jobs. See [`docs/REPRODUCIBLE_STARTUP_MILESTONE.md`](docs/REPRODUCIBLE_STARTUP_MILESTONE.md) for the verified acceptance proof.

## Safety boundaries

- Repository investigation is read-only until explicit approval.
- Patch generation performs no repository write.
- An approved patch is tied to one deterministic remediation identity.
- Duplicate approvals reuse existing successful remediation state instead of creating duplicate branches or PRs.
- Stale/ambiguous source state fails closed.
- High-risk merge/deploy/destructive actions remain recommendation-only.
- Passing CI never triggers automatic merge or claims production recovery.
- `main` is not the development branch for this build.

## Development branch

Active implementation branch: `agent-build-core`

Draft integration PR: `agent-build-core` → `develop`

See [`docs/IMPLEMENTATION_PROGRESS.md`](docs/IMPLEMENTATION_PROGRESS.md) for the verified feature/status ledger.

# Reproducible Startup Milestone

Status: **IMPLEMENTED + VERIFIED**

## Goal

A teammate or judge machine should be able to take a clean checkout of `agent-build-core`, validate the environment, install the same declared dependency set, run the project checks, and start the MVP without memorizing backend/frontend setup commands.

## Windows operator path

```text
fresh checkout
→ verify.bat (optional full acceptance)
→ start.bat
→ environment preflight
→ .env bootstrap if missing
→ backend/.venv creation
→ pinned Python dependencies
→ locked npm ci install
→ backend health wait
→ frontend start
→ READY
```

Stop with `stop.bat`.

## Reproducibility controls

- Python runtime marker: `.python-version` = `3.11`
- Node runtime marker: `.nvmrc` = `22.23.2`
- exact direct Python requirements in `backend/requirements.txt`
- exact direct frontend/tooling versions in `frontend/package.json`
- full npm dependency tree committed in `frontend/package-lock.json` (lockfile v3 + integrity hashes)
- bootstrap requires the lockfile and runs `npm ci`
- `.env` is copied from `.env.example` only when absent and remains ignored
- local launcher state is kept in ignored `.run/`

## Acceptance proof

GitHub Actions run #288 on implementation head `b5bbff64ea09c52e728bbb6d4899234c98eeda5f` completed successfully:

```text
Ubuntu backend compile: PASS
Ubuntu backend tests: 51 passed, 0 failures
Ubuntu locked npm ci: PASS
Ubuntu frontend TypeScript/Vite build: PASS
Windows strict preflight: PASS
Windows clean bootstrap: PASS
Windows clean-clone acceptance: 3/3 PASS
```

The Windows acceptance creates the virtual environment and installs dependencies from a clean GitHub checkout before running backend compile, the full backend test suite, and the frontend production build.

## Important boundary

The committed npm lockfile freezes the full frontend dependency graph. The Python file exactly pins the project's direct Python packages, but pip still resolves their transitive dependencies; a later production-grade packaging phase should add a fully hashed Python transitive lock if required.

This milestone proves reproducible setup/build acceptance. It does not prove live GitHub write credentials are present on an arbitrary machine; live remediation still requires an authenticated GitHub CLI session or a suitable local token.

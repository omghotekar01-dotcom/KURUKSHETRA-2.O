# KURUKSHETRA 2.0 HACKFEST 2026

**Team Members:**
- Om Ghotekar
- Nikhil Jadhav
- Om Patil
- Yash Nale

This is the shared `develop`-branch workspace for our 4-person Kurukshetra 2.0 Hackfest project.
> The default `main` branch must remain stable and submission-safe. Do not develop directly on `main`.

## Current Phase

**Setup / pre-problem-statement**

The exact problem statement, architecture, stack and individual work ownership will be finalized after the hackathon problem statements are released.

## Start Here

Before doing substantial work, read:

1. [`docs/TEAM_README.md`](docs/TEAM_README.md) — collaboration rules, Git workflow and repository safety
2. [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — live source of truth for completed, in-progress and remaining work
3. [`docs/COLLABORATION_TEST.md`](docs/COLLABORATION_TEST.md) — safe teammate push/PR access test

## Branching Model

```text
main
  ↑
develop
  ↑
feature/*  fix/*  docs/*  test/*
```

### Rules

- `main` = stable/demo/submission branch
- `develop` = shared integration branch
- all real development happens in dedicated feature/fix/docs/test branches
- completed work is merged by Pull Request into `develop`
- only tested integrated builds move from `develop` to `main`

## Before Starting Any Task

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<clear-task-name>
```

Do not overwrite or restructure existing project files without first understanding the shared architecture and contracts.

## Commit Standard

Examples:

```text
feat(api): add analysis endpoint
feat(ui): add result dashboard
feat(db): add history model
fix(api): validate empty input
test(api): add endpoint tests
docs(readme): update setup instructions
```

Avoid meaningless commits such as `final`, `changes`, `done`, `final2` or `working`.

## Continuity Across ChatGPT / Codex / Astra

`docs/PROJECT_STATUS.md` is the handoff file.

Any AI coding session should first inspect:

- current repository structure
- current branch
- latest commits
- `docs/TEAM_README.md`
- `docs/PROJECT_STATUS.md`
- existing API/database/shared contracts

After a meaningful milestone, update `docs/PROJECT_STATUS.md` so another teammate or coding session can continue without guessing what has already been done.

## Repository Safety

Never:

- force-push shared branches
- commit `.env` or secrets
- silently change API/database contracts
- delete another teammate's files
- rewrite the entire app to add one feature
- experiment directly on `main`

If a shared contract must change, document it explicitly as a **BREAKING CHANGE**.

## Current Repository Status

See [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the live checklist and handoff state.

---

**Important:** This repository is currently public. Files committed to `develop` are not confidential even though the default GitHub page opens `main` first.
>>>>>>> origin/develop

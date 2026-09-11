# KURUKSHETRA 2.0 HACKFEST 2026 — TEAM WORKING GUIDE

> Internal working guide for the 4-person hackathon team. This file lives on the `develop` branch so the default `main` branch stays clean and stable. Note: the repository is public, so this file is not confidential.

## Event Context

- Event: Kurukshetra 2.0 Hackfest 2026
- Venue: MIT Arts, Commerce & Science College, Alandi, Pune
- Mode: Offline
- Dates: 11–12 September 2026
- Duration: 24 hours
- Team size: 4
- Problem statements release: 11:00 AM on 11 September 2026

## Team Operating Principle

We are building ONE shared product. Work will be divided only after the final problem statement, idea, architecture and module boundaries are decided.

Before coding:

1. Understand the problem statement.
2. Refine the idea.
3. Freeze the MVP and P0/P1/P2 features.
4. Freeze the architecture and stack.
5. Define API/data/database contracts.
6. Divide work among four members.
7. Create feature branches.
8. Build in parallel.
9. Merge through pull requests into `develop`.
10. Merge only stable, tested code from `develop` into `main`.

## Git Branch Model

```text
main
  ↑
develop
  ↑
feature/*  fix/*  docs/*  test/*
```

### `main`

- Stable/demo/submission branch only.
- Never experiment directly on `main`.
- Never rewrite the project structure directly on `main`.
- Merge into `main` only when the integrated build is tested.

### `develop`

- Shared integration branch.
- All feature PRs target `develop` first.
- This branch may move quickly, but should remain reasonably runnable.

### Feature branches

Create one branch per logical task/module, for example:

```text
feature/backend-core
feature/frontend-dashboard
feature/database
feature/ai-pipeline
feature/api-integration
fix/api-validation
docs/readme
test/integration
```

Do not use a single personal branch for dozens of unrelated changes. Prefer small logical branches that can be reviewed and merged safely.

## Safe Start Before Every Task

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<clear-task-name>
```

If the branch already exists:

```bash
git checkout feature/<clear-task-name>
git merge develop
```

## Commit Standard

Use meaningful Conventional Commit style messages:

```text
feat(api): add prediction endpoint
feat(ui): add analytics dashboard
feat(db): add result history model
fix(api): validate missing input
test(api): add endpoint tests
docs(readme): add setup instructions
refactor(service): isolate scoring logic
```

Avoid commits such as `final`, `changes`, `done`, `final2`, or `working`.

## Pull Request Rule

Every completed feature should normally go:

```text
feature/* -> develop
```

A PR description should include:

- What was implemented
- Files/modules changed
- Dependencies added
- API changes
- Database changes
- How to test
- Known issues
- Screenshots if UI-related

After integration and testing:

```text
develop -> main
```

## Repository Safety Rules

Once the project skeleton and shared contracts are finalized:

- Do not rename major folders casually.
- Do not delete another member's files.
- Do not rewrite the repository from scratch to add one feature.
- Do not silently change shared API routes or JSON keys.
- Do not silently change database fields/relationships.
- Do not hardcode secrets.
- Do not force-push `main` or `develop`.
- Do not use destructive resets on shared work unless the team explicitly agrees.
- Do not commit `.env`, API keys, credentials, tokens or private keys.

Before any shared contract change, clearly mark it as a **BREAKING CHANGE** and explain affected modules.

## Integration Rule

Do not wait until the final hours to merge everything.

Recommended milestones:

1. Basic frontend ↔ backend connection
2. Backend ↔ database
3. Core algorithm/AI/data module integration
4. Full user workflow
5. Stable demo release

The team should aim for an ugly but working end-to-end MVP early, then improve it.

## Documentation Rule

Documentation is continuous, not a last-hour task.

Expected docs may include:

```text
docs/
├── TEAM_README.md
├── PROJECT_STATUS.md
├── architecture.md
├── api-contract.md
├── database-schema.md
├── testing.md
└── demo-script.md
```

## AI Assistant / Codex / Astra Continuity Rule

Whenever any AI assistant works on this repository, it must first inspect the current repository state before changing files.

It must preserve:

- current directory structure
- current API contracts
- current database schema
- existing working modules
- shared configuration

For every implementation, the assistant should report:

1. Task
2. Files changed
3. Dependencies added
4. Run/test commands
5. Expected result
6. Git branch
7. Recommended commit message
8. Integration impact
9. Next recommended step

The current global project state is maintained in `docs/PROJECT_STATUS.md`. Read that file before starting substantial new work and update it after meaningful milestones.

## Demo Reliability

If the final project depends on internet, cloud, APIs, LLMs, live sensors or remote models, build a deterministic fallback/demo path where practical.

The judging demo must not depend on one fragile external service.

## Final Submission Standard

Before submission we want:

- Working end-to-end application
- Stable `main`
- Integrated `develop`
- Meaningful commit history
- README/setup instructions
- `.env.example` if required
- Architecture documentation
- API/database documentation
- Tests
- Screenshots/demo data
- Metrics where relevant
- Demo script
- Fresh-clone test
- Final release/tag

## Current Phase

The exact problem statement and individual task ownership have not yet been frozen. Do not invent permanent member responsibilities until the team explicitly records them in `docs/PROJECT_STATUS.md`.

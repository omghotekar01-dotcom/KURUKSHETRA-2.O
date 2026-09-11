# DEPLOYMENT, OPERATIONS AND FALLBACKS

Last updated: 2026-09-11
Status: **PROVISIONAL**

## Goal

The hackathon build must be runnable on a fresh machine, resilient to partial service failure, and demonstrable even if internet/API integrations are unreliable.

## Deployment principle

Prefer the simplest deployment that supports a reliable demo.

Recommended options:
- frontend: Vercel/Netlify or local Vite dev server;
- backend: Render/Railway/Fly.io or local FastAPI/Uvicorn;
- database: PostgreSQL if stable and quick, otherwise SQLite/local fallback;
- RAG index: local file/FAISS index committed or generated from sample data;
- external tools: only those required by the final demo.

## Local-first run path

Target commands should eventually be reducible to something like:

```bash
# backend
python -m venv .venv
# activate venv
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

Exact commands must be replaced after project structure is frozen.

## Demo modes

### LIVE MODE
Uses real configured services such as:
- hosted LLM;
- GitHub API;
- Gmail/Slack integration;
- hosted database.

### DEMO MODE
Uses deterministic/local substitutes:
- known incident examples;
- local runbook/index;
- canned-but-schema-valid integration response where external action cannot be guaranteed;
- SQLite/local memory;
- fixed evaluation scenarios.

Demo mode must be clearly labeled and must not pretend a fake external action was real.

## Failure matrix

| Failure | Expected fallback |
|---|---|
| LLM API unavailable | deterministic/sample result or retry + clear error |
| GitHub API unavailable | show prepared local repo/evidence fixture; disable real action |
| Gmail/Slack unavailable | draft notification and record unsent state |
| PostgreSQL unavailable | SQLite/local JSON fallback if implemented |
| Vector index missing | rebuild from committed sample corpus or simple keyword fallback |
| Internet unavailable | local demo golden path remains usable |
| One agent node fails | incident becomes `INCONCLUSIVE/ESCALATED`, not falsely resolved |

## Health checks

Backend should expose a lightweight endpoint such as:

```text
GET /health
```

Optionally report non-secret dependency status:
- API running;
- DB reachable;
- RAG index loaded;
- external integrations configured/not configured.

Do not expose credentials or raw environment values.

## Logging

Minimum useful logs:
- request/incident ID;
- workflow stage;
- tool invoked;
- latency;
- success/failure;
- policy/approval decision;
- verification result.

Do not log:
- API keys;
- OAuth tokens;
- full secrets;
- unnecessary sensitive user data.

## Fresh-clone acceptance test

Before submission:
1. clone into a new folder;
2. follow README only;
3. install dependencies;
4. configure `.env` from `.env.example`;
5. start backend/frontend;
6. run demo scenario;
7. confirm no local-only hidden files are required.

## Backup demo assets

Keep:
- deterministic sample incidents;
- screenshots of main flow;
- short screen recording if event rules allow;
- architecture image/diagram;
- expected demo outputs;
- local runbook/evaluation fixtures.

## Release discipline

- development happens away from `main`;
- integration occurs in `develop`;
- freeze major architectural changes before final hours;
- only tested integrated build goes to `main`;
- final tagged version recommended, e.g. `v1.0-hackathon`.

## Production future scope

A real startup version would need substantially stronger infrastructure:
- proper authentication/tenant isolation;
- secrets manager;
- durable queues/checkpointing;
- audit log immutability;
- rate limiting;
- role-based tool permissions;
- observability;
- backups/migrations;
- formal incident/action policies;
- security review.

Do not pretend the 24-hour prototype has these properties unless actually implemented.
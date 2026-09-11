# PROMPT LIBRARY

These prompts are reusable operating templates. Fill in the bracketed sections from the current project state; do not blindly use placeholders.

---

## P-01 — Deep Research / Market Gap Hunter

Act as a principal researcher, SRE architect, developer-tools product strategist and skeptical startup analyst. We are building a 24-hour hackathon prototype that may become a startup. Research the current state of AI incident response, AI debugging, autonomous coding, SRE agents, observability, RAG for engineering, human-in-the-loop automation and incident memory.

Project context:
[INSERT CURRENT PRODUCT THESIS]

Your job:
1. Search recent first-party product docs, engineering blogs, papers and credible open-source projects.
2. Build a capability map of what already exists.
3. Identify features that are already commodity and must not be called novel.
4. Identify unsolved workflow, trust, safety, evaluation, cost or accessibility gaps.
5. Find failure cases and limitations, not only success stories.
6. Rank opportunities by user value, differentiation and 24-hour feasibility.
7. Produce 3 strongest product wedges and explain what we should NOT build.
8. Provide evidence sources and dates for important claims.
9. Translate findings into exact changes to `PRODUCT_STRATEGY.md`, `COMPETITOR_GAPS.md` and `EXPERIMENT_BACKLOG.md`.

Never claim uniqueness without checking competitors. Never recommend complexity only because it sounds advanced.

---

## P-02 — Problem Statement Judge

We received this exact hackathon PS:

[PASTE PS]

Our current idea:

[PASTE IDEA]

Act as a hackathon judge + staff engineer + product manager. Score the idea 0–10 on PS fit, originality, real-world value, technical depth, 24-hour feasibility, demo impact, measurable outcome, scalability, safety and differentiation.

Then:
- identify hidden PS requirements;
- identify any way our idea drifts from the PS;
- compare against obvious existing solutions;
- state GO / MODIFY / DROP;
- if MODIFY, preserve the strongest core and remove distractions;
- define the one-sentence product thesis;
- define P0/P1/P2;
- define the golden-path demo;
- list the five questions judges are most likely to attack.

Do not write code yet.

---

## P-03 — Architecture Freeze

Act as a principal software architect designing a 24-hour implementation for:

[PRODUCT]

Constraints:
[TEAM / TIME / PS / ALLOWED SERVICES]

Current repo structure:
[PASTE TREE]

Produce:
1. architecture diagram;
2. frontend/backend/agent/data boundaries;
3. exact shared schemas;
4. API contract;
5. DB entities;
6. agent state;
7. integration interfaces;
8. failure modes and fallbacks;
9. security boundaries;
10. testing strategy;
11. module ownership boundaries suitable for four parallel developers;
12. merge/integration order.

Optimize for minimal merge conflicts and a working golden path by T+4–6 hours.

Do not restructure existing working code unless you explicitly explain the migration cost.

---

## P-04 — Evidence-Backed RCA Designer

Design the incident reasoning layer. Input:
[INCIDENT SCHEMA]

Available evidence:
[RUNBOOKS / GITHUB / LOGS / HISTORY]

Create a structured RCA system that returns multiple hypotheses instead of one opaque answer.

Each hypothesis must contain:
- title;
- confidence;
- evidence_for IDs;
- evidence_against IDs;
- missing information;
- next diagnostic action;
- proposed remediation only if justified.

Requirements:
- confidence must decrease when evidence conflicts;
- no historical fix may be presented as certain merely because similarity is high;
- novel incidents must be allowed to return “insufficient evidence”;
- output must be valid structured JSON/Pydantic-compatible data;
- include test cases with misleading/noisy evidence.

---

## P-05 — RAG Engineer

We need local/low-cost incident retrieval using:
- runbooks;
- resolved incidents;
- optionally GitHub issues.

Design a hackathon-feasible RAG pipeline using Sentence Transformers + FAISS unless another local approach is clearly superior.

Provide:
- chunk/data format;
- metadata fields;
- embedding strategy;
- category/environment filters;
- top-k policy;
- minimum relevance threshold;
- duplicate handling;
- novel-incident fallback;
- retrieval evaluation dataset;
- top-1/top-3 metrics;
- caching strategy;
- exact Python modules and tests.

Avoid a vector database service unless it materially improves the 24-hour build.

---

## P-06 — Agent Safety / Approval Designer

Act as an AI-agent security architect. Review the planned actions below:
[LIST ACTIONS]

Classify each as LOW / MEDIUM / HIGH risk based on reversibility, blast radius, data sensitivity and production impact.

Design a policy where:
- AI cannot approve/merge/deploy its own generated changes;
- branch protection remains authoritative;
- destructive/production actions fail closed;
- every action records rationale, evidence, confidence and approval;
- external/untrusted text cannot silently instruct tools;
- credentials are least privilege;
- demo mode cannot accidentally mutate real production infrastructure.

Return exact policy rules, backend schemas, UI states and tests.

---

## P-07 — GitHub Integration Engineer

Build a GitHub integration for the project with strict scope.

Goal:
[READ ISSUES / RECENT COMMITS / CREATE ISSUE / CREATE DRAFT PR]

Repository workflow:
- `main` stable;
- `develop` integration;
- teammate branches;
- no direct autonomous writes to main;
- no auto-merge.

For implementation provide:
- minimum GitHub permissions required;
- API endpoints/library methods;
- backend service interface;
- retry/error behavior;
- demo fallback;
- security notes;
- tests/mocks;
- exact files and commit message.

Never request broader permissions than needed.

---

## P-08 — Frontend Product Designer

Act as a senior developer-tools UX designer and React engineer. Build a judge-facing UI for an AI incident-response platform.

The judge must understand within 30 seconds:
- what incident happened;
- severity and owner;
- what evidence was gathered;
- likely root causes and confidence;
- recommended fix;
- risk of the action;
- whether human approval is needed;
- what action happened;
- whether verification passed.

Screens:
[LIST CURRENT SCREENS]

Use the existing API contract and do not invent incompatible response fields. Start with contract-matching mocks if backend is not ready. Prioritize information hierarchy and visible system intelligence over decorative animation.

For every change give exact files, run/test commands, branch and commit message.

---

## P-09 — Evaluation Lab Builder

Act as an ML/agent evaluation engineer. Build a reproducible benchmark for the incident-response agent.

Create at least:
- category-routing scenarios;
- retrieval scenarios;
- RCA scenarios;
- misleading/noisy evidence scenarios;
- novel incident scenarios;
- unsafe-action scenarios;
- verification pass/fail scenarios.

For each define expected outputs/ranges. Implement a runner that produces machine-readable JSON plus summary metrics.

Metrics may include:
- routing accuracy;
- top-k retrieval hit rate;
- RCA top-1/top-3;
- unsafe-action block rate;
- verification success rate;
- latency.

Never tune only to one demo case. Preserve failing examples.

---

## P-10 — Integration / Merge Guardian

You are the integration lead. Before merging [BRANCH] into `develop`:

1. inspect changed files;
2. identify contract/schema/API changes;
3. identify overlap with other branches;
4. run or specify tests;
5. check env/dependency changes;
6. check secrets;
7. check whether README/status docs need update;
8. predict likely merge conflicts;
9. state MERGE / FIX FIRST;
10. if FIX FIRST, provide minimum safe patch.

Never resolve a conflict by blindly choosing one side. Preserve working behavior from both branches.

---

## P-11 — Demo Reliability Engineer

Design the final 3–5 minute demo so it still works if internet, LLM, Gmail, GitHub or a remote database fails.

Current golden path:
[PASTE]

Provide:
- exact demo incident;
- expected values/results;
- pre-seeded historical incident/runbook;
- live-mode path;
- demo-mode fallback;
- screenshots/recording checklist;
- failure recovery script;
- reset procedure;
- what each teammate should do if a component fails during judging.

The demo must never depend on improvisation.

---

## P-12 — Judge Q&A Red Team

Act as an extremely skeptical senior hackathon judging panel with expertise in SRE, AI, security and startups.

Project:
[SUMMARY]

Architecture:
[SUMMARY]

Claims/metrics:
[PASTE]

Ask 30 difficult questions covering:
- novelty;
- competitor comparison;
- why agents are required;
- hallucination;
- data quality;
- model choice;
- evaluation;
- safety;
- privacy;
- cost;
- scalability;
- deployment;
- what is real vs mocked;
- team contribution;
- 24-hour build evidence;
- business model.

Then provide concise, technically defensible answers. Flag any question where our current evidence is insufficient instead of inventing an answer.

---

## P-13 — Startup Critic

Assume the hackathon is over and we want to turn this into a startup.

Evaluate:
- ICP;
- buyer vs user;
- current alternatives;
- switching cost;
- integration burden;
- moat;
- data advantage;
- willingness to pay;
- security/compliance barrier;
- onboarding time;
- measurable ROI;
- path from prototype to product.

Give a 90-day validation roadmap and identify what NOT to build before customer interviews.

---

## P-14 — Status / Handoff Prompt

Read:
- `docs/PROJECT_STATUS.md`;
- `TEAM_BRAIN/DECISION_LOG.md`;
- latest relevant code/contracts;
- latest commits/PRs.

Return only:
1. current working state;
2. what is complete;
3. blockers;
4. risky inconsistencies;
5. next 5 tasks in priority order;
6. which branch each task belongs on;
7. tests required before integration.

Do not invent completed work.

---

## P-15 — Research Update Prompt

Search for significant developments since the last `RESEARCH_LEDGER.md` update in AI incident response, debugging agents, SRE agents, coding agents, observability, agent safety and evaluation.

For each meaningful finding:
- cite a first-party/primary source;
- summarize capability/finding;
- explain whether it makes one of our ideas commodity;
- identify a new gap/opportunity;
- recommend an experiment or product change;
- update `SOURCES.md` and the relevant strategy file.

Skip marketing noise and duplicate findings.

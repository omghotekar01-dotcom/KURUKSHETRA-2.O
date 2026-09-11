# KURUKSHETRA 2.0 — DOCUMENTATION ROUND ULTRA MASTER PROMPT

Use this prompt in ChatGPT/Codex/Astra/other AI only after providing the official documentation template or its headings. The purpose is to generate a truthful, judge-ready PDF submission for the Kurukshetra 2.0 Documentation Round.

---

## MASTER PROMPT

You are acting as a senior technical writer, startup product architect, AI/ML engineer, software architect, hackathon mentor, research analyst, QA lead and judge-facing documentation specialist for **Kurukshetra 2.0 Hackfest 2026**.

Your task is to create a complete, professional, technically credible, concise-but-detailed documentation submission for our selected problem statement and solution. The output must be suitable for conversion to PDF and submission to the hackathon organizing/judging team.

### Event context

- Event: Kurukshetra 2.0 Hackfest 2026
- Organizer/Venue: MIT Arts, Commerce & Science College, Alandi, Pune, Maharashtra
- Mode: Offline, 24-hour hackathon
- Team size: 4
- Documentation Round: online submission during the hackathon
- Documentation must explain the selected problem statement and the solution being developed
- Required themes explicitly include: problem analysis, research, proposed solution, technical flow, technology stack, implementation, innovation, references, and use of external/AI resources
- Official documentation template may be supplied separately; when supplied, its structure/order is authoritative
- Submission format: PDF
- Team Leader submits the final PDF

### Repository / source of truth

Repository:
`https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O`

During active development, use the `develop` branch as the documentation/integration source of truth. `main` is stable/submission-only.

If repository access is available, read these first:
1. `TEAM_BRAIN/A_TO_Z_INDEX.md`
2. `TEAM_BRAIN/CANONICAL_PROJECT_DESCRIPTION.md`
3. `TEAM_BRAIN/PROJECT_DESCRIPTION_TEMPLATES.md`
4. `TEAM_BRAIN/PRODUCT_STRATEGY.md`
5. `TEAM_BRAIN/WORKFLOW_AND_AGENT_SPEC.md`
6. `TEAM_BRAIN/TECH_STACK_AND_DEPENDENCIES.md`
7. `TEAM_BRAIN/ARCHITECTURE_PLAYBOOK.md`
8. `TEAM_BRAIN/ARCHITECTURE_RESEARCH.md`
9. `TEAM_BRAIN/COMPETITOR_GAPS.md`
10. `TEAM_BRAIN/RAG_AND_KNOWLEDGE_DESIGN.md`
11. `TEAM_BRAIN/DATA_API_AND_STATE_CONTRACTS.md`
12. `TEAM_BRAIN/SECURITY_AND_GUARDRAILS.md`
13. `TEAM_BRAIN/EVALUATION_FRAMEWORK.md`
14. `TEAM_BRAIN/CLAIMS_AND_EVIDENCE_LEDGER.md`
15. `TEAM_BRAIN/RESEARCH_LEDGER.md`
16. `TEAM_BRAIN/SOURCES.md`
17. `TEAM_BRAIN/DEMO_PITCH_AND_JUDGE_QA.md`
18. `docs/PROJECT_STATUS.md`

Never override fresher repository information with this prompt.

### Critical truthfulness rule

The current project direction may still be provisional until the exact selected problem statement is frozen. Do not fabricate the final problem statement, project name, measured metrics, implemented features, model training results, deployment status, or integrations.

Every claim in the document must belong to one of these states:
- **Implemented / working now**
- **Currently being implemented**
- **Planned within hackathon scope**
- **Future scope**

Never present planned/future features as already implemented.

If the exact selected Problem Statement is not supplied, stop before writing the final document and request:
`PASTE THE EXACT SELECTED PROBLEM STATEMENT / ID / DOMAIN HERE.`

If the official documentation template is not supplied, generate a structured draft using the fallback section structure below, but clearly state that it must be mapped into the official template before submission.

---

## CURRENT WORKING PRODUCT DIRECTION

Unless superseded by the final PS/repository, the current concept under investigation is a startup-level **agentic engineering incident-response platform**.

### One-line working pitch

**An AI incident commander that investigates across code, history and runbooks, ranks likely root causes, proposes remediation, gates risky actions through human approval, verifies outcomes, and remembers what worked.**

### Simple problem

Software teams often lose significant time during incidents because information is fragmented across bug reports, repository history, logs, runbooks, old incidents, notifications and individual engineer memory. A developer may have to manually determine what failed, severity, owner, recent changes, whether the issue occurred before, likely root cause, safe next action and whether that action actually resolved the incident.

### Proposed lifecycle

```text
Incident / Bug / CI Failure / Logs
        ↓
Normalize and structure
        ↓
Classify category + component + severity + likely owner
        ↓
Collect evidence from permitted sources
        ↓
Retrieve similar historical incidents / runbooks
        ↓
Generate ranked root-cause hypotheses
        ↓
Generate remediation options + verification plan
        ↓
Risk / confidence / policy gate
        ↓
Human approval where required
        ↓
Execute a bounded action
        ↓
Verify result
        ↓
Update incident timeline + structured memory
```

### Target product principle

This is not intended to be a generic chatbot or a simple bug-classifier/email-sender. The intended value is a closed-loop, evidence-backed and auditable incident workflow.

### Candidate differentiators

Use only those still supported by the final architecture:
1. Evidence-backed RCA with source/provenance visibility.
2. Multiple ranked hypotheses instead of pretending one answer is certain.
3. Risk-aware action gating based on consequence as well as confidence.
4. Human approval for consequential changes.
5. Verification as a separate step after action execution.
6. Structured incident memory containing verified outcomes for future retrieval.
7. Evaluation/benchmark capability rather than demo-only anecdotes.
8. Lightweight startup/team-friendly architecture instead of requiring a massive observability stack.

### Likely prototype users

Provisional target: small-to-medium software/SaaS engineering teams using GitHub, runbooks and lightweight engineering workflows, especially teams without a large dedicated SRE organization.

Final target users must be adjusted to the exact selected PS.

---

## PROVISIONAL TECH STACK

Use the final repository state if different.

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Axios
- Recharts
- React Router

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

### Agent / AI orchestration
- LangGraph
- selected LangChain components only where useful

### LLM
- Fast hosted LLM suitable for hackathon latency (for example Groq-hosted Llama-family model if chosen)
- Structured JSON/Pydantic outputs
- deterministic/demo fallback where practical

### RAG / Retrieval
- Sentence Transformers
- lightweight embedding model such as `all-MiniLM-L6-v2` if retained
- FAISS or NumPy cosine similarity depending final corpus size

### Persistence
- PostgreSQL if stable within hackathon time
- SQLite/local fallback for deterministic demo mode

### Integrations
- GitHub REST API / PyGithub where required
- MCP or direct tool APIs where appropriate
- notifications such as Gmail/Slack only if actually implemented/needed

### Testing
- Pytest
- FastAPI TestClient/httpx
- Vitest
- Playwright for critical end-to-end path if time permits

Do not claim every item is implemented unless verified from the current repo/status.

---

## AGENT / MODULE DESIGN

The desired workflow may use logical modules such as:
1. Intake Normalizer
2. Triage Agent
3. Evidence Collector
4. Retrieval/RAG Agent
5. Root Cause Analysis Agent
6. Remediation Agent
7. Deterministic Risk/Policy Engine
8. Human Approval Gate
9. Bounded Execution Adapter
10. Verification Agent
11. Memory Writer

These are logical responsibilities; do not falsely claim eleven separate LLMs are running if some are combined or deterministic.

### Intended state lifecycle

```text
NEW
→ TRIAGING
→ INVESTIGATING
→ RCA_READY
→ REMEDIATION_READY
→ AWAITING_APPROVAL (when needed)
→ EXECUTING
→ VERIFYING
→ RESOLVED
```

Alternative outcomes may include:
`ESCALATED`, `FAILED_ACTION`, `INSUFFICIENT_EVIDENCE`, `REJECTED`.

---

## SAFETY / RESPONSIBLE AI PRINCIPLE

Documentation should explicitly explain that:
- recommendation is separated from authorization;
- high-risk changes are not silently executed;
- least-privilege integrations are preferred;
- GitHub changes should be branch/PR scoped rather than direct writes to `main`;
- evidence, recommendation, confidence, action, approval and result should be auditable;
- external incident text/logs are treated as untrusted input;
- secrets are never exposed in prompts/logs/repository;
- failed safety checks should fail closed where appropriate;
- human oversight remains part of consequential decisions.

This is both a technical design advantage and a responsible-AI requirement.

---

## RESEARCH / COMPETITOR POSITIONING

Do not write weak claims like:
`No such solution exists.`

Modern observability, incident-response and AI coding platforms already provide significant AI-assisted investigation capabilities. Therefore our differentiation must be described precisely and defensibly.

Frame the gap around the final combination actually built, for example:
- lightweight deployment for smaller engineering teams;
- evidence transparency;
- multiple hypotheses;
- safe action gating;
- human-in-the-loop authorization;
- post-action verification;
- structured incident memory;
- measurable evaluation;
- workflow integration at lower operational complexity.

Only claim uniqueness supported by current research and the final product.

---

## DOCUMENT GENERATION RULES

### Rule 1 — Official template wins

If I provide the official organizer documentation template (DOCX/PDF/images/text headings):
- preserve its exact section order;
- preserve mandatory headings;
- answer every field;
- do not remove mandatory declarations;
- adapt content length to available space;
- create extra subsections only where allowed;
- ensure final output can be exported cleanly to PDF.

### Rule 2 — Judge-friendly writing

Write like a strong engineering team, not like marketing AI.

Avoid:
- meaningless adjectives;
- “revolutionary”, “100% accurate”, “guaranteed”, “world’s first” unless proved;
- repetitive paragraphs;
- generic explanations of AI;
- fake metrics;
- unexplained buzzwords.

Prefer:
- concrete pain;
- explicit user;
- precise workflow;
- measurable objectives;
- diagrams/tables;
- evidence;
- tradeoffs;
- honest current implementation status.

### Rule 3 — Technical depth

For every major technical component explain:
1. input;
2. processing;
3. output;
4. reason for technology choice;
5. fallback/failure behavior;
6. how it integrates with other components.

### Rule 4 — External / AI resource disclosure

Create a truthful section called **External Tools, Open-Source Components and AI Assistance** (or map it to the template equivalent).

Separate:
- frameworks/libraries;
- pretrained/open models;
- APIs/services;
- external repositories used only for research/inspiration;
- AI assistants used during development/documentation;
- datasets/knowledge sources if any.

For each, state HOW it was used.

Do not imply that inspiration/reference code was originally authored by us.

The public repository `whitespace-24/Agentic-Bug-Router-and-Dispatcher` may be mentioned as **reference/inspiration only** if relevant. Our submission must not be represented as a near-copy.

### Rule 5 — References

Use credible, traceable references.
Prefer:
- official documentation;
- primary papers;
- first-party product documentation;
- authoritative GitHub repositories.

Use a consistent citation style suitable for the organizer template. Never invent URLs, papers, authors, statistics or publication dates.

### Rule 6 — Implementation status

Include an implementation-progress table if the template allows:

| Module | Status | Evidence / Current Output | Remaining Work |
|---|---|---|---|

Populate only using verified repo/project status.

### Rule 7 — Visuals

Where supported, include clean diagrams for:
- problem/current workflow;
- proposed workflow;
- system architecture;
- agent graph/state flow;
- data/RAG flow;
- safety approval flow;
- user journey.

Use Mermaid/text diagrams if generating source text. Avoid unreadable dense diagrams.

---

## FALLBACK DOCUMENT STRUCTURE WHEN OFFICIAL TEMPLATE IS NOT YET PROVIDED

Generate these sections in this order:

1. **Cover Page**
   - Hackathon name
   - Project title (if frozen)
   - Problem Statement ID/title/domain
   - Team name
   - Team leader/member names only if supplied
   - Institution only if supplied
   - Repository link if allowed

2. **Executive Summary**
   - 150–250 words
   - problem + user + solution + core innovation + expected outcome

3. **Selected Problem Statement**
   - exact text/ID/domain
   - interpretation in our own words
   - constraints

4. **Problem Analysis**
   - who experiences the problem
   - current workflow
   - pain points
   - root causes
   - why existing manual/current methods are insufficient

5. **Research and Background**
   - existing approaches/products/research
   - what already works
   - remaining gaps
   - evidence/sources

6. **Target Users and Stakeholders**
   - primary user
   - secondary stakeholder
   - jobs-to-be-done

7. **Proposed Solution**
   - simple explanation
   - one-line pitch
   - exact end-to-end workflow

8. **Objectives and Success Criteria**
   - P0 objectives
   - measurable indicators

9. **Core Features**
   - P0
   - P1
   - future/P2 clearly separated

10. **Innovation and USP**
   - what is technically or workflow-wise different
   - why it matters
   - competitor-gap mapping

11. **System Architecture**
   - high-level architecture diagram
   - component explanations
   - data flow

12. **Agentic Workflow / AI Logic**
   - each logical module/agent
   - deterministic vs LLM responsibilities
   - structured state
   - confidence/uncertainty

13. **RAG / Knowledge Layer**
   - knowledge sources
   - embeddings/index
   - retrieval
   - provenance
   - low-confidence fallback

14. **Risk / Approval / Verification Layer**
   - action risk levels
   - human approval
   - bounded execution
   - verification

15. **Technology Stack**
   - table: layer, technology, role, why chosen

16. **Data Model / API / Integrations**
   - major entities
   - key endpoints/interfaces
   - external tools

17. **Implementation Methodology**
   - repository structure
   - Git collaboration model
   - branches
   - module integration
   - testing approach

18. **Current Implementation Status**
   - implemented
   - in progress
   - planned before final demo

19. **Testing and Evaluation**
   - benchmark incidents
   - routing/RAG/RCA/safety metrics
   - golden-path end-to-end test

20. **Security, Privacy and Responsible AI**
   - permissions
   - secrets
   - auditability
   - human control
   - prompt injection/untrusted input

21. **Feasibility**
   - why it can be built within hackathon scope
   - fallbacks
   - offline/demo mode

22. **Scalability and Production Evolution**
   - how prototype can evolve without pretending it is already production-grade

23. **Startup / Business Potential**
   - user/buyer
   - value proposition
   - adoption wedge
   - future business model hypotheses

24. **Limitations**
   - current technical/AI/integration limits

25. **Future Scope**
   - only genuinely future features

26. **External Tools, Open-Source Components and AI Assistance**
   - transparent disclosure

27. **References**
   - properly formatted sources

28. **Appendix** (only if useful)
   - API examples
   - schema
   - detailed benchmark/test scenarios
   - screenshots

---

## REQUIRED INPUT BLOCK

Before final generation, use the following information. Never guess blank factual fields.

```text
EXACT SELECTED PROBLEM STATEMENT:
[PASTE]

PROBLEM STATEMENT ID:
[PASTE]

DOMAIN:
[PASTE]

OFFICIAL DOCUMENTATION TEMPLATE / HEADINGS:
[UPLOAD OR PASTE]

FINAL/WORKING PROJECT NAME:
[PASTE IF FROZEN]

TEAM NAME:
[PASTE]

TEAM MEMBERS:
[PASTE IF REQUIRED BY TEMPLATE]

INSTITUTION:
[PASTE IF REQUIRED]

CURRENT IMPLEMENTATION STATUS:
[READ REPO OR PASTE LATEST]

MANDATORY WORD/PAGE LIMITS:
[PASTE]

ANY ORGANIZER-SPECIFIC DECLARATIONS:
[PASTE]
```

If repository access is available, derive implementation status from the repo rather than asking again.

---

## FINAL OUTPUT INSTRUCTIONS

After receiving the exact PS + official template:

1. First perform a **template compliance audit** and list every mandatory field internally.
2. Read the repository/current status.
3. Identify any factual gaps that cannot safely be inferred.
4. Ask only for truly missing mandatory facts.
5. Generate the complete final documentation in the exact template order.
6. Make the writing concise, human, technical and judge-friendly.
7. Use tables/diagrams where they improve clarity.
8. Mark planned vs implemented features correctly.
9. Include transparent AI/external-resource disclosure.
10. Include real references only.
11. Check consistency between problem, solution, architecture, stack and implementation status.
12. Run a final **anti-hallucination / claim audit**.
13. Run a **judge-objection audit**: identify statements likely to be challenged and tighten them.
14. Run a **PDF-readability audit**: headings, table overflow, diagram readability, spacing and page breaks.
15. Return a submission-ready document plus a short final checklist of any fields the team must manually verify before uploading.

### Absolute prohibition

Do not invent:
- PS wording;
- organizer requirements;
- team/member facts;
- implemented features;
- evaluation metrics;
- dataset size;
- accuracy;
- user counts;
- cost savings;
- citations;
- awards/validation;
- production deployments.

If evidence does not exist, describe the item as a target, hypothesis, planned evaluation or future scope.

### Quality bar

The documentation should make a judge understand, within a few minutes:
1. What exact problem are we solving?
2. Who has the problem?
3. Why does it matter?
4. What already exists?
5. What exactly are we building?
6. Why is our approach meaningfully different?
7. How does it technically work?
8. What have we actually implemented?
9. How will we prove it works?
10. How do we prevent unsafe/incorrect actions?
11. Can it realistically scale into a useful product?
12. What external/AI resources did we use?

Generate the documentation to satisfy those questions before optimizing for visual decoration.

# PROJECT DESCRIPTION TEMPLATES

Last updated: 2026-09-11
Status: **PROVISIONAL — REPLACE WITH FINAL PS-SPECIFIC WORDING AFTER FREEZE**

Purpose: keep every teammate, README, form, PPT, LinkedIn-style summary and judge response consistent.

## 10-second description

We are building an agentic engineering incident-response system that turns a raw software incident into evidence-backed root-cause hypotheses, a risk-aware remediation plan, a controlled action and a verified outcome.

## 20-second description

Software teams waste time reconstructing incident context across bug reports, code history, runbooks and previous issues. Our system acts like an AI incident commander: it classifies the incident, gathers evidence, retrieves similar past cases, ranks likely root causes, proposes remediation, gates risky actions through human approval, executes a bounded action and verifies whether it worked.

## 30-second judge description

Our project is not just a bug classifier or chatbot. It is a closed-loop incident-response workflow. A user submits a bug or incident; the system identifies severity and ownership, gathers evidence from approved sources such as runbooks, historical incidents and GitHub context, generates ranked root-cause hypotheses, proposes a fix with confidence and risk, pauses for human approval when needed, executes a safe bounded action such as creating an issue or draft PR, and then verifies the result. Resolved incidents become structured memory for future cases.

## 60-second technical description

The current architecture uses a web dashboard with a FastAPI backend and a stateful agent workflow. Incident input is normalized into a structured state, then triaged for category, severity and ownership. An evidence layer retrieves relevant runbooks, historical incidents and optional repository context. RAG and an RCA component produce ranked hypotheses with provenance rather than a single opaque answer. A remediation module creates candidate actions and a deterministic risk/policy layer decides whether the action is allowed, requires human approval or must remain recommendation-only. Approved low/medium-risk actions can be executed through bounded integrations such as GitHub or team messaging. Verification is a separate stage: an action being executed does not automatically mean the incident is resolved. The verified outcome is stored as structured incident memory and used for future retrieval/evaluation.

## 60-second business description

Engineering teams often spend more time gathering context than actually fixing incidents. Large enterprises can buy sophisticated SRE platforms, but smaller product teams still juggle GitHub, runbooks, alerts and human memory. Our startup thesis is a lightweight incident-response coordination layer that turns fragmented evidence into a safe, auditable workflow. The core value is faster triage, reuse of previous incident knowledge, safer AI-assisted remediation and verification of what actually worked. The product can begin with GitHub-native teams and later expand into richer observability and policy integrations.

## README-style overview

**Working concept:** Agentic Engineering Incident Response

The platform helps software teams investigate and respond to incidents through an auditable closed loop:

```text
Incident
→ Triage
→ Evidence Collection
→ Historical Retrieval
→ Root-Cause Hypotheses
→ Remediation
→ Risk / Approval
→ Bounded Action
→ Verification
→ Incident Memory
```

The system is designed around evidence, uncertainty, human control and verification rather than blind autonomous remediation.

## Problem statement mapping template

Replace placeholders after PS release:

> **Problem Statement:** [EXACT PS]
>
> The PS requires [MANDATORY OUTCOME]. Existing workflows struggle because [PAIN]. Our solution addresses this by [CORE FLOW]. The most important differentiator is [USP], while keeping the build feasible in 24 hours through [SCOPE DECISION].

## One-line value proposition templates

- From incident to evidence-backed action in minutes — with humans controlling risky steps.
- Investigate faster, act safer, and remember what actually fixed the incident.
- Turn fragmented engineering context into a verifiable incident-response workflow.

Use only one final tagline after branding is frozen.

## Technical novelty template

Avoid:
> “We use AI, RAG and agents.”

Prefer:
> “We combine traceable evidence, multiple RCA hypotheses, action-risk gating, human approval and post-action verification in one closed loop.”

## Startup differentiator template

> Mature observability vendors already provide AI investigation. Our wedge is [FINAL GAP], designed specifically for [TARGET USER] with [SETUP/COST/SAFETY/WORKFLOW ADVANTAGE].

Do not fill this with a claim that is contradicted by competitor research.

## Form/application description — 100–150 words

Software incidents often force engineers to reconstruct context across bug reports, code changes, runbooks and historical incidents before they can safely act. Our proposed platform is an agentic incident-response layer that structures the incident, classifies severity and ownership, retrieves relevant organizational knowledge, generates evidence-backed root-cause hypotheses and proposes remediation. Unlike a normal chatbot, it separates recommendation from authorization: risky actions pass through a policy and human-approval gate. Bounded actions such as creating a GitHub issue, draft PR or team notification can then be executed and independently verified. The verified resolution is stored as structured incident memory, allowing future incidents to be investigated faster. The hackathon prototype focuses on one reliable end-to-end workflow, explainability, safety, measurable evaluation and a deterministic demo fallback.

## Description consistency rules

Every public/project description must clearly distinguish:
- implemented now;
- currently being built;
- planned future scope.

Never describe P2 ideas as already working.
Never claim training if only using pretrained models/RAG.
Never claim production autonomy if the prototype uses approval/recommendation-only high-risk actions.
Never claim measured impact until `CLAIMS_AND_EVIDENCE_LEDGER.md` contains the supporting result.
# RESEARCH LEDGER

Last updated: 2026-09-11

Purpose: continuously capture current market/research evidence, what it means for our project, and what not to reinvent.

## 2026 market reality

### 1. AI SRE is already a serious product category

Current platforms are no longer limited to summarizing alerts. Mature systems investigate production incidents across logs, metrics, traces, infrastructure metadata, deployment history and other context.

Implication: “AI classifies a bug and sends an email” is not enough novelty. Our differentiation must come from workflow, evidence quality, safety, verification, accessibility or a distinctive user segment.

### 2. Datadog Bits Investigation

Datadog describes Bits Investigation as an autonomous SRE agent that reasons across metrics, logs, traces, infrastructure metadata, network telemetry and monitor configuration to triage and remediate root causes. Datadog also emphasizes evaluation infrastructure because improvements on one investigation type can silently degrade other cases.

Design implication:
- We need multi-source evidence rather than only runbook RAG.
- We need an evaluation suite, not one impressive demo.
- More tool calls do not automatically mean better RCA; noisy evidence can actively hurt.
- Our agent should rank evidence and hypotheses rather than dump all retrieved context into one prompt.

### 3. PagerDuty SRE Agent

PagerDuty’s SRE Agent focuses on automating the repetitive early minutes of incident response: ingest event data, runbooks and diagnostics, surface likely root causes, recommend remediation, recall similar incidents and preserve learning. PagerDuty engineering also emphasizes long-running investigations, real-time updates and human steering during the investigation.

Design implication:
- Show investigation progress and evidence updates in the UI.
- Allow a human to add a hypothesis or steer the investigation.
- Incident memory and learning should be first-class, not an afterthought.

### 4. Rootly AI

Rootly AI connects incident data with third-party observability, code, infrastructure, feature flags, tickets and documentation, and can operate from Slack. It emphasizes reducing context switching during incidents.

Design implication:
- “Single pane of glass” is valuable, but mature products already do it.
- For hackathon scope, integrate only a few high-value sources deeply rather than many shallow connectors.
- A credible differentiation could be lightweight cross-tool evidence fusion for smaller teams.

### 5. incident.io

incident.io positions AI across the incident lifecycle: initial diagnosis, triage, investigation, collaboration and post-incident learning. It can reason over recent code changes and past team actions.

Design implication:
- Lifecycle coverage is commodity at enterprise level.
- Our strongest unique element should be a specific closed-loop workflow or safety/evaluation capability rather than generic “AI throughout the incident lifecycle.”

### 6. Sentry Seer

Sentry’s Seer can use runtime context such as errors, spans, logs, environment details and commits to identify root causes, propose solutions, generate code changes and open pull requests. In 2026 Sentry added integrations that can hand bugs with full context to Claude or GitHub Copilot for fixing.

Design implication:
- Repo-aware RCA + code fix is already real.
- We should not claim “creates a PR from an error” as novel by itself.
- A possible gap is safer, evidence-scored remediation and verification across sources, especially for teams that lack Sentry-grade telemetry.

### 7. GitHub coding agents

GitHub Copilot coding agents can take an issue, work in a cloud development environment, modify code, validate with tests/linters, push changes and create or update pull requests. GitHub explicitly preserves human review and repository security controls.

Design implication:
- We should integrate with existing coding-agent workflows rather than rebuild a full autonomous coding environment from scratch.
- Our system can generate a structured remediation package or branch/PR request and let a coding agent implement it.
- Branch protection and approval must remain part of the architecture.

## Current problem opportunities

### A. Evidence fragmentation

Incident information is split across issue text, logs, telemetry, recent deployments, code, chat threads, runbooks and historical tickets. Engineers spend valuable time reconstructing context.

Opportunity: create a normalized “Incident Evidence Graph” that records evidence objects, source, time, confidence, affected component and relationship to hypotheses.

### B. Root-cause overconfidence

Many AI tools produce one clean answer even when evidence is incomplete or contradictory.

Opportunity: maintain multiple hypotheses with evidence-for, evidence-against, confidence and next-best diagnostic action. Judges can visibly see disciplined reasoning instead of opaque LLM output.

### C. Unsafe autonomous action

Agentic remediation can modify code or systems incorrectly. Industry security guidance increasingly stresses scoped credentials, sandboxing, branch protection, separation of duties and human approval.

Opportunity: introduce an Action Risk Gate:
- LOW: create note, issue, notification, draft PR;
- MEDIUM: code patch / configuration change requiring review;
- HIGH: deployment, production restart, DB mutation — never auto-executed in hackathon prototype.

### D. Verification gap

Recommendation systems often stop at “here is a fix.”

Opportunity: every proposed remediation gets a verification plan and status. For code changes this can mean unit tests, lint, sample reproduction or a simulated health check.

### E. Incident memory quality

A naive memory stores text. A useful memory stores symptoms, environment, root cause, action, evidence, success/failure, time-to-resolution and confidence.

Opportunity: create structured incident memory that improves future retrieval and can explain exactly why an older incident is relevant.

### F. Evaluation of agent behavior

Autonomous agent quality can regress silently. Datadog publicly describes needing a real-world evaluation platform for SRE agents.

Opportunity: ship an “Evaluation Lab” in the hackathon product with 10–30 deterministic incident scenarios and a scorecard. This is unusual in student projects and demonstrates engineering maturity.

## Differentiation candidates

Ranked by value vs 24-hour feasibility:

1. Evidence-backed multi-hypothesis RCA — HIGH value, feasible.
2. Structured incident memory + similar-case retrieval — HIGH value, feasible.
3. Risk-aware human approval gate — HIGH value, feasible.
4. GitHub-aware remediation package / issue / draft PR — HIGH demo value, feasible.
5. Verification/test feedback loop — HIGH value, moderate complexity.
6. Agent evaluation dashboard — HIGH judge value, moderate complexity.
7. Live log/telemetry connectors — useful but integration-heavy.
8. Fully autonomous code repair — flashy but high risk/time.
9. Production deployment automation — not appropriate for hackathon safety.

## Research questions still open

- Exact Kurukshetra problem statement and judging rubric.
- Which external integrations are allowed/available on hackathon network.
- Whether GitHub Issues/PR actions should be real or demo-mode.
- What minimum telemetry format can produce convincing RCA without building observability infrastructure.
- Best benchmark set for routing/RCA/fix verification.
- How to quantify confidence calibration simply enough for a judge demo.
- Whether a graph-based evidence model materially improves the demo over structured JSON/PostgreSQL.
- Which product wedge is strongest: startups/SMBs, college DevOps teams, SaaS engineering teams, or internal enterprise engineering.

## Research discipline for future updates

For each new source, add:
- date;
- product/research name;
- first-party source;
- capability/finding;
- direct implication;
- whether it makes one of our planned features commodity;
- resulting action or experiment.

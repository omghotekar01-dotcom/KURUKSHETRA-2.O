# COMPETITOR / GAP MAP

Last updated: 2026-09-11

This document prevents us from presenting already-common capabilities as unique.

## Datadog Bits Investigation

Observed capability:
- autonomous incident investigation;
- reasons over logs, metrics, traces, infrastructure metadata and more;
- root-cause analysis and remediation support;
- serious internal evaluation platform for agent quality.

Do not claim as novel:
- “AI reads telemetry and finds root cause.”

Possible gap for us:
- lightweight GitHub/runbook-first deployment for teams without a full Datadog stack;
- visible multi-hypothesis evidence scoring;
- action-risk gate and verification-oriented workflow;
- benchmark/evaluation transparency in a compact product.

## PagerDuty SRE Agent

Observed capability:
- incident/runbook/log analysis;
- likely root causes;
- recommended diagnostics/remediation;
- memory of previous incidents;
- long-running collaborative investigation.

Do not claim as novel:
- “AI incident commander remembers previous incidents.”

Possible gap for us:
- deeper GitHub-native code/remediation workflow for small teams;
- explicit evidence graph and hypothesis comparison;
- low-cost self-host/local mode;
- verification and action-risk scoring as first-class UX.

## Rootly AI

Observed capability:
- incident AI inside Slack;
- connects incident data with observability, code, infrastructure, feature flags, tickets and docs;
- gathers evidence across tools and reports in the incident channel.

Do not claim as novel:
- “One AI agent connects all engineering tools.”

Possible gap:
- narrower but deeper incident-to-code loop;
- transparent risk/approval policy;
- reproducible evaluation lab;
- structured memory focused on successful fixes.

## incident.io AI

Observed capability:
- AI across alerting, triage, investigation, collaboration and postmortem;
- can use recent code changes and past team actions.

Do not claim as novel:
- “AI covers the whole incident lifecycle.”

Possible gap:
- technical RCA/remediation workflow over broader incident management;
- evidence quality and verification;
- developer-centric rather than incident-command-centric experience.

## Sentry Seer

Observed capability:
- root-cause analysis using runtime context and code;
- solution generation;
- code changes;
- opening pull requests;
- handing context to Claude/GitHub Copilot.

Do not claim as novel:
- “AI identifies a bug and creates a PR.”

Possible gap:
- multi-source evidence outside Sentry telemetry;
- explicit uncertainty/hypothesis competition;
- human approval policies based on action risk;
- structured incident-memory loop;
- generic GitHub/startup-friendly deployment.

## GitHub Copilot coding agents

Observed capability:
- issue-to-code workflow;
- branch/PR-based autonomous coding;
- testing/linting in development environment;
- review-driven iteration.

Do not build from scratch:
- a complete cloud coding-agent platform.

Use instead:
- our system generates high-quality incident context, RCA, acceptance criteria and verification plan;
- coding agent can receive that package;
- our product verifies/records the result.

## Strategic conclusion

The broad category is crowded. A winning project cannot be “AI + RAG + bug routing.”

Our product should focus on a distinctive combination:

**Incident Evidence Graph + Ranked RCA Hypotheses + Risk-Aware Action Gate + Verification Loop + Structured Incident Memory + Evaluation Lab.**

This combination is more defensible because it focuses on trustworthy decision quality rather than simply adding another autonomous agent.

## Judge answer: “How are you different from Sentry/PagerDuty/Datadog?”

Suggested answer structure:

1. Acknowledge that enterprise tools already offer strong AI incident capabilities.
2. State our wedge rather than pretending they do not exist.
3. Explain that our prototype is GitHub/runbook-first and lightweight.
4. Show transparent evidence/hypotheses instead of only a generated answer.
5. Show that autonomy is controlled by risk and human approval.
6. Show actual verification of a remediation.
7. Show a measurable evaluation page proving the agent on multiple incidents.

Avoid statements such as “no one has done this before.”
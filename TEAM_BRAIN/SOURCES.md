# SOURCE INDEX

Last updated: 2026-09-11

Use first-party sources wherever possible. The purpose is not to collect links endlessly; each source should support a specific design or competitive conclusion.

## AI SRE / Incident Response

### Rootly — What Is an AI SRE Agent? How AI Is Changing Incident Response in 2026
https://rootly.com/sre/ai-sre-agent-ai-changing-incident-response-2026

Use for: current AI-SRE category framing, automation of detection/resolution, incident toil.

### Rootly — AI connectors / evidence across stack
https://rootly.com/changelog/rootly-ai-gathers-incident-evidence-across-your-stack

Use for: evidence gathering across observability, code, infrastructure, feature flags, ticketing and documentation.

### Rootly — AI Agent in Slack
https://rootly.com/changelog/rootly-ai-agent-in-slack

Use for: incident-channel agent UX and context-switch reduction.

### PagerDuty — SRE Agent
https://support.pagerduty.com/main/docs/sre-agent

Use for: runbooks, diagnostics, recurring incidents, likely causes, remediation and incident memory.

### PagerDuty Engineering — Inside PagerDuty’s SRE Agent
https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/

Use for: long-running investigation, real-time progress, human steering and architecture constraints.

### Datadog — Building Bits AI SRE
https://www.datadoghq.com/blog/building-bits-ai-sre/

Use for: autonomous investigation across telemetry, causal reasoning, noise problems and incident-resolution claims.

### Datadog — Evaluation platform for autonomous SRE agents
https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/

Use for: why agent evaluation/regression infrastructure matters.

### Datadog — Incident AI documentation
https://docs.datadoghq.com/incident_response/incident_management/investigate/incident_ai/

Use for: incident investigation workflows, linked telemetry and Slack/web incident collaboration.

### Datadog — AI in Incident Response
https://www.datadoghq.com/blog/datadog-incident-response-ai-features/

Use for: fragmented incident context across telemetry, deployments and conversations.

### incident.io — AI Platform
https://incident.io/ai-platform

Use for: current lifecycle coverage across alerting, triage, investigation and collaboration.

### incident.io — Postmortems
https://docs.incident.io/post-incident/postmortems-overview

Use for: post-incident learning and the cost of reconstructing context from multiple systems.

## AI Debugging / Code Remediation

### Sentry — Seer GA
https://sentry.io/changelog/seer-sentrys-ai-debugger-is-generally-available/

Use for: runtime context, root cause, suggested fixes and automated PR creation.

### Sentry — Seer across development stages
https://sentry.io/changelog/seer-now-debugs-in-every-stage-of-development/

Use for: value of runtime context over source-code-only debugging.

### Sentry API — Start Seer Issue Fix
https://docs.sentry.io/api/seer/start-seer-issue-fix/

Use for: concrete root-cause → solution → code changes → PR pipeline.

### Sentry — Seer + Claude Agent
https://sentry.io/changelog/seers-claude-integration-is-now-generally-available/

Use for: handing rich issue context to a coding agent to implement a fix and create PR.

### Sentry — Seer + GitHub Copilot
https://sentry.io/changelog/seer-can-send-bugs-to-github-copilot-for-the-fix-now-in-open-beta/

Use for: existing bug-to-coding-agent handoff capability.

### Sentry — GitLab support
https://sentry.io/changelog/seer-supports-gitlab/

Use for: code-context RCA and merge-request generation beyond GitHub.

## Coding Agents / GitHub

### GitHub Docs — Manage issues and PRs with Copilot
https://docs.github.com/en/copilot/how-tos/github-copilot-app/managing-issues-and-pull-requests

Use for: issue-to-agent-to-PR workflow.

### GitHub Docs — Kick off Copilot agent task
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task

Use for: branch/PR behavior and task execution model.

### GitHub Changelog — Ask Copilot to change a PR
https://github.blog/changelog/2026-03-24-ask-copilot-to-make-changes-to-any-pull-request/

Use for: autonomous code modifications, tests/linters and PR iteration.

### GitHub Changelog — Resolve merge conflicts with Copilot
https://github.blog/changelog/2026-03-26-ask-copilot-to-resolve-merge-conflicts-on-pull-requests/

Use for: current agent capability around PR maintenance.

### GitHub Docs — Review Copilot output
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output

Use for: human review and workflow security expectations.

### GitHub — Coding Agent press release / security model
https://github.com/newsroom/press-releases/coding-agent-for-github-copilot

Use for: branch protection, controlled internet access, human approval and MCP integration.

### GitHub Docs — Third-party coding agents
https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents

Use for: current ecosystem of external coding agents integrated into GitHub.

### GitHub Docs — Rationale, confidence and approvals
https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-automation-rationale-and-approvals

Use for: rationale/audit trail/confidence/approval patterns.

## Agent Security / Governance

### OWASP AISVS — AI Secure Coding / autonomous agent controls
https://github.com/OWASP/AISVS/blob/main/1.0/en/0x92-Appendix-C_AI_for_Code_Generation.md

Use for: separation of duties, preventing agent self-approval/merge/deploy, branch protection and scoped identities.

### Microsoft Agent Governance Toolkit — Action-bound approval protocol
https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/adr/0030-action-bound-approval-protocol.md

Use for: approval binding, immutable approval chains and fail-closed execution concepts.

### Microsoft VS Code docs — Secure AI-assisted development
https://github.com/microsoft/vscode-docs/blob/main/docs/agents/run/security.md

Use for: terminal/tool/URL approval, sandboxing and risks of bypassing approvals.

### AWS sample autonomous coding agents — Security design
https://github.com/aws-samples/sample-autonomous-cloud-coding-agents/blob/main/docs/design/SECURITY.md

Use for: isolated sessions, least privilege, branch-scoped blast radius and human review.

## Reference Project

### Agentic Bug Router & Dispatcher
https://github.com/whitespace-24/Agentic-Bug-Router-and-Dispatcher

Use for: simple LangGraph + Groq + local RAG + Gmail MCP bug-routing reference architecture. Do not treat this repository as the final project or copy it as-is.

## Source-quality rule

When making major design claims:
1. prefer official docs / engineering posts;
2. verify publication date/current capability;
3. avoid relying on generic SEO comparison pages;
4. record what the source actually proves;
5. never convert vendor marketing claims into our measured results.
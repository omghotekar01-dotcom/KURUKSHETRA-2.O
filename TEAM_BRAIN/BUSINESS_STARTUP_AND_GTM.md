# BUSINESS, STARTUP AND GO-TO-MARKET HYPOTHESIS

Last updated: 2026-09-11
Status: **PROVISIONAL — DO NOT OVERSELL DURING HACKATHON**

## Startup thesis

Engineering teams increasingly use AI for coding and operations, but incident response still requires expensive context reconstruction and cautious human judgment. A useful startup wedge is not “another chatbot for logs”; it is a lightweight incident-response coordination layer that combines evidence, historical memory, risk-aware action and verification.

## Provisional beachhead market

Small-to-mid SaaS/startup engineering teams that:
- use GitHub;
- have basic monitoring/logs/runbooks;
- do not have a large dedicated SRE organization;
- repeatedly lose developer time to triage and context switching;
- are interested in automation but unwilling to give agents unrestricted production access.

## Buyer / champion hypotheses

Possible economic buyer:
- CTO / VP Engineering / Head of Engineering.

Possible internal champion:
- engineering lead;
- SRE/DevOps lead;
- on-call platform engineer.

Primary daily user:
- developer/on-call engineer.

## Value proposition

Potential value pillars:
1. reduce time to triage;
2. reduce repeated investigation;
3. improve reuse of historical incident knowledge;
4. make AI recommendations explainable/auditable;
5. automate low-risk coordination actions;
6. verify whether remediation actually worked.

## Why not just use ChatGPT?

A standalone chat lacks durable incident state, organization-specific evidence, action permissions, approval policy, structured history, verification and integrated workflows. The product value must come from those system capabilities rather than from generic language generation.

## Why not simply use Sentry/Datadog/PagerDuty?

Those platforms already provide sophisticated incident/observability capabilities. The project must not claim those problems are unsolved. Potential gaps/wedges include:
- lightweight GitHub-native setup for smaller teams;
- transparent evidence graph + uncertainty representation;
- cross-tool incident memory focused on verified outcomes;
- explicit risk-aware approval gateway for AI remediation;
- reproducible evaluation visible to the customer;
- lower-cost/local-friendly deployment.

See `COMPETITOR_GAPS.md` for detailed market reality.

## Pricing hypotheses — future only

Possible future models:
- free/local developer tier;
- team SaaS by engineer/month;
- usage/incident-based tier;
- enterprise tier for private deployment, policy controls and audit retention.

Do not build billing for the hackathon.

## Go-to-market hypotheses

### Wedge 1 — GitHub-native startups
Offer fast installation around GitHub issues/CI failures + runbooks, then add incident memory and integrations.

### Wedge 2 — Repeated incident memory
Sell the ability to stop solving the same production issue from scratch.

### Wedge 3 — Safe agent gateway
Organizations may use multiple AI coding/ops agents but need centralized approval, evidence and audit controls.

## Adoption strategy

A strong product should provide value before deep integration:
1. paste incident/logs;
2. connect GitHub optionally;
3. upload/add runbooks;
4. get evidence-backed triage;
5. later connect richer telemetry.

Reducing setup friction is itself a competitive advantage.

## Moat hypotheses

Weak moat:
- prompts;
- generic LLM classification;
- prettier dashboard.

Stronger possible moat:
- structured verified incident memory unique to each organization;
- outcome feedback/evaluation datasets;
- policy/action governance layer;
- integrations and workflow embedding;
- high-quality evidence linking and calibration;
- trust built through verification/audit.

## Market validation questions

Future customer interviews should ask:
- How many incidents/week require manual triage?
- Where is context currently spread?
- Which step consumes most time?
- What incident knowledge is lost after resolution?
- Which actions would users allow AI to take automatically?
- Which actions would always need approval?
- What existing tools are already paid for?
- What integration would make switching/adding a tool worthwhile?

## Why now

The timing hypothesis is that coding agents and AI-SRE products are making autonomous engineering actions normal enough to be useful, while safety/approval/evaluation remain major trust constraints. This creates room for products that focus on controlled, evidence-backed automation rather than unrestricted autonomy.

This is a hypothesis and must be supported by current sources/market research in `RESEARCH_LEDGER.md` and `SOURCES.md`.

## Hackathon business story

Keep it simple:
- clear user;
- painful repetitive workflow;
- measurable time/context saved;
- differentiated safe workflow;
- credible path from hackathon prototype to SaaS.

Do not spend pitch time on TAM fantasy or invented revenue numbers unless judges explicitly ask.
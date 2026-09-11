# NON-FUNCTIONAL REQUIREMENTS

Last updated: 2026-09-11
Status: **PROVISIONAL**

## Reliability
- Golden demo path must be repeatable.
- Failure of one external service must not crash the entire application.
- Unsupported/low-confidence cases should degrade to escalation, not fabricated certainty.

## Performance
Prototype targets, to be measured rather than promised:
- UI feedback/loading indicator should appear immediately after submission.
- Individual agent/tool stages should expose progress.
- End-to-end demo latency should remain comfortable for live judging.
- Cache static embeddings/indexes instead of recomputing unnecessarily.

## Security
- No secrets in repository/logs.
- Least-privilege integration credentials.
- Human approval for consequential actions.
- No production auto-deploy/merge.
- External content treated as untrusted.

Authoritative policy: `SECURITY_AND_GUARDRAILS.md`.

## Auditability
For significant actions store:
- incident ID;
- evidence used;
- hypothesis/recommendation;
- confidence/risk;
- approval decision;
- tool/action result;
- verification result;
- timestamps.

## Explainability
Users should be able to inspect why a hypothesis/action was proposed using visible evidence/provenance. A numeric confidence alone is insufficient.

## Maintainability
- modular components;
- shared schemas;
- centralized configuration;
- clear branch ownership;
- minimal duplication;
- typed/validated interfaces where practical.

## Portability
- documented Windows/Linux/macOS-friendly setup where practical;
- no hidden local paths;
- fresh-clone test before submission;
- `.env.example` for required configuration.

## Usability
- core workflow understandable within ~30 seconds;
- clear status/progress;
- explicit error/failure messages;
- no dead controls;
- approval actions clearly worded.

## Accessibility minimum
- adequate contrast;
- readable typography;
- labels beyond color alone;
- keyboard-accessible primary actions where practical.

## Reproducibility
- deterministic fixtures;
- fixed benchmark cases;
- documented dependency versions/lockfiles;
- repeatable setup/run/test commands.

## Scalability story — future, not prototype claim
A startup version should be able to evolve toward:
- more incidents/tenants;
- durable queues/checkpoints;
- richer vector/index infrastructure;
- RBAC and tenant isolation;
- multiple integrations;
- policy engine;
- stronger observability.

Do not implement enterprise infrastructure merely to claim scalability.

## Privacy/data minimization
- store only data necessary for incident workflow/evaluation;
- avoid sending secrets/raw sensitive logs to external LLMs where not needed;
- future product should support redaction/tenant policies/private deployment options.

## Availability targets
No production SLA is claimed for the hackathon prototype. The only enforceable target is reliable local/demo operation during judging.

## Finalization after PS/build
Replace vague goals with measured values for:
- p50/p95 workflow latency;
- supported concurrent users if relevant;
- index/query latency;
- maximum fixture/corpus size tested;
- browser/device support;
- actual recovery behavior.
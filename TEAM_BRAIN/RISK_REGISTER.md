# RISK REGISTER

Last updated: 2026-09-11
Status: ACTIVE

Purpose: track risks that can kill the hackathon build, invalidate claims, or make the demo unsafe/unreliable.

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Exact PS does not fit current incident-response concept | Medium | Critical | Treat current idea as provisional; perform GO/MODIFY/DROP decision immediately after PS release |
| Overbuilding too many agents/features | High | Critical | Freeze golden path and P0 first; P2 only after stable MVP |
| Integration delayed until final hours | High | Critical | First end-to-end integration early; merge frequently into `develop` |
| LLM output breaks parser | Medium | High | Structured/Pydantic output; validate and fail gracefully |
| External API/LLM unavailable during demo | Medium | High | Labeled deterministic demo mode/local fixtures |
| GitHub/OAuth integration consumes too much time | Medium | High | Implement one bounded integration deeply; retain mock/schema-compatible fallback |
| RAG retrieves misleading similar incident | Medium | High | Score/threshold/provenance; treat retrieval as evidence, not truth |
| Agent proposes unsafe remediation | Medium | Critical | Deterministic risk gate + human approval + no high-risk auto-execution |
| Secrets committed to public repo | Medium | Critical | `.env`, `.gitignore`, `.env.example`, scan status before commits |
| Teammate overwrites project structure/contracts | Medium | High | branch discipline, PRs, breaking-change rule, shared docs |
| Duplicate/conflicting AI-generated code | High | High | inspect repo first, scoped ownership, minimal patches, contracts |
| Judges view idea as a clone of existing AI-SRE tools | Medium | Critical | competitor-aware positioning and explicit differentiation |
| Judges view reference repo as copied | Medium | Critical | build original architecture/code/UX; use reference only for learning |
| No measurable evidence | Medium | High | maintain benchmark and capture actual metrics before pitch |
| Fancy UI while backend golden path is broken | Medium | High | ugly end-to-end MVP before visual polish |
| Database/cloud setup failure | Medium | Medium | SQLite/local fallback |
| Live demo data accidentally looks fake | Medium | Medium | clearly label demo mode/fixtures; show real integration only when real |
| Multiple hypotheses confuse users | Low | Medium | rank clearly, show evidence, select top recommendation while exposing uncertainty |
| Slow agent latency makes demo awkward | Medium | High | measure node latency, cache embeddings, reduce calls, stream progress |
| Runbook corpus too tiny/unconvincing | Medium | Medium | curated diverse scenarios; explain prototype scale honestly |
| Unsupported claims about market/competitors | Medium | High | source claims in `SOURCES.md`; separate facts from hypotheses |
| Production-like action causes real damage | Low | Critical | non-production/demo targets, least privilege, explicit approval, no deploy/merge |
| User-provided issue text contains prompt injection | Medium | High | treat external text as untrusted data; restrict tool permissions and system policy |
| New research causes endless architecture churn | High | High | decision log + freeze point; only change when evidence materially improves project |
| Final README/setup incomplete | Medium | High | fresh-clone test and checklist before submission |
| No working fallback laptop/environment | Low/Medium | High | local run path, committed fixtures, backup screenshots/video if permitted |

## Risk review cadence

Revisit this register when:
- exact PS is chosen;
- architecture is frozen;
- any new external integration is added;
- first full integration completes;
- feature freeze begins;
- final demo is rehearsed.

## Escalation rule

Any risk that can break the P0 golden path within the remaining time outranks cosmetic features. Fix/mitigate it before adding P2 scope.
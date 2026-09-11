# GLOSSARY AND ACRONYMS

Last updated: 2026-09-11

Use these meanings consistently across README, PPT, code comments, judge answers and AI sessions.

## Agent
A software component that uses a model and/or deterministic logic to pursue a bounded task, often with tools and state. Do not call every function an agent.

## Agentic workflow
A stateful multi-step process in which the system can reason over context, choose/sequence bounded actions, use tools, pause for approvals and react to results.

## AI SRE
Use cautiously. Broadly refers to AI systems supporting site reliability / incident investigation and remediation. Mature vendors already use this term.

## API
Application Programming Interface. In this project mainly REST endpoints between frontend/backend or integrations.

## Approval gate / Human-in-the-loop (HITL)
A workflow pause requiring a human to approve, edit or reject a consequential action before execution.

## Audit trail
Recorded evidence of what the system observed, proposed, approved, executed and verified, with timestamps/identities where applicable.

## Blast radius
Potential scope of harm/impact if an action or failure affects systems/users.

## Closed-loop incident response
The full cycle: detect/intake → understand → investigate → recommend → approve/act → verify → learn, rather than stopping at a suggestion.

## Confidence
An estimate of certainty for a classification/hypothesis. It is not authorization and must not be treated as proof.

## Evidence
A traceable fact/source used to support or challenge a hypothesis: runbook entry, historical incident, commit, log snippet, user input, etc.

## Evidence graph
A proposed product representation connecting evidence objects to root-cause hypotheses and actions. This is a differentiator concept, not automatically implemented.

## FAISS
Facebook AI Similarity Search. Library for efficient vector similarity search; optional for hackathon-scale RAG.

## Golden path
The smallest end-to-end workflow that must work reliably in the demo.

## Incident
A software/service problem requiring investigation/response. Can originate from user bug report, CI failure, monitoring alert, support complaint, etc.

## Incident memory
Structured record of previous verified incidents including symptoms, actual root cause, action and verification, used for future retrieval.

## LangGraph
Framework for stateful graph-based agent/workflow orchestration, useful for conditional routing, persistence and human approval.

## LLM
Large Language Model used for tasks such as classification, summarization, hypothesis generation and drafting.

## MCP
Model Context Protocol. A protocol/ecosystem for exposing tools/context to AI applications. In the reference bug-router project it is used to access Gmail tooling.

## MVP
Minimum Viable Product. For this hackathon: the smallest reliable end-to-end product that proves the core value.

## P0 / P1 / P2
- P0: must work for valid submission/demo.
- P1: strong value after P0 is stable.
- P2: wow/future features only after core stability.

## Provenance
Information about where evidence/data came from so users can inspect/verify it.

## RAG
Retrieval-Augmented Generation. Retrieve relevant organization-specific knowledge/evidence first, then use it to ground model generation/reasoning.

## RCA
Root Cause Analysis. Process of determining why an incident occurred. The prototype should represent uncertainty rather than claiming every RCA is certain.

## Remediation
Action proposed/taken to reduce or resolve the incident.

## Risk gate
Policy layer that determines whether a proposed action is low/medium/high risk and whether it may execute, requires approval, or is forbidden.

## Runbook
Documented procedure/known issue-resolution guidance used by engineers during incidents.

## Semantic similarity
Similarity based on meaning rather than exact words, usually using embeddings/vectors.

## Structured output
Model output constrained to a schema (e.g. JSON/Pydantic) instead of fragile free text parsing.

## Verification
A check proving whether the intended outcome occurred after a remediation/action. Action success and incident resolution are different concepts.

## Vector embedding
Numeric representation of text/objects that allows semantic similarity search.

## Vector database/index
System used to store/search embeddings. FAISS can act as a local index; a separate managed vector DB is not required for small hackathon data.

## Terms we should avoid misusing

- **Training** — do not say we trained a model if we only prompted or used RAG.
- **Autonomous production remediation** — do not claim this if high-risk actions are recommendation-only.
- **100% accurate** — never claim without rigorous evidence; practically avoid absolute accuracy claims.
- **Patentable/unique in the world** — do not claim without proper novelty search/legal review.
- **Real-time** — use only if latency/streaming behavior truly supports it.
- **Self-learning** — structured incident memory/retrieval is not the same as model retraining.
- **Blockchain/Web3/cloud-native** — do not add labels unless the actual architecture/PS requires them.
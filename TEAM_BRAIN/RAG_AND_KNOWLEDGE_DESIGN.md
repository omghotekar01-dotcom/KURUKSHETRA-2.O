# RAG AND KNOWLEDGE DESIGN

Last updated: 2026-09-11
Status: **PROVISIONAL**

## Purpose

Define how the project should use retrieval and incident memory without turning RAG into a buzzword.

## Knowledge sources — prototype priority

1. Curated runbooks / known issue→fix pairs.
2. Structured historical incidents created by the demo system.
3. GitHub issues/PR context when integration is enabled.
4. Optional documentation snippets supplied for the chosen PS.

Do not ingest arbitrary huge corpora just to claim scale.

## Canonical knowledge object

Each reusable incident/runbook entry should ideally include:

- `id`
- `title`
- `category`
- `component`
- `environment`
- `symptoms`
- `error_signatures`
- `root_cause`
- `resolution`
- `verification`
- `tags`
- `source`
- `created_at`
- `resolved_at`
- optional `embedding`

## Retrieval flow

```text
incident summary + extracted error hints
        ↓
normalize query
        ↓
embedding model
        ↓
vector search / similarity
        ↓
metadata/category filters where useful
        ↓
Top-K candidates
        ↓
rerank / threshold
        ↓
return evidence with provenance
```

## Hackathon implementation

Preferred default:
- `sentence-transformers`
- `all-MiniLM-L6-v2` or another small embedding model
- FAISS or in-memory cosine search depending dataset size
- structured JSON/SQLite/PostgreSQL metadata

For a tiny curated dataset, simple NumPy similarity is acceptable and easier to debug. Upgrade to FAISS only if it improves clarity/performance.

## Retrieval safety rules

- A similar incident is evidence, not proof that the same root cause applies.
- Return similarity/relevance score visibly.
- Use a threshold / low-confidence fallback.
- If no strong match exists, say so.
- Preserve the exact retrieved source text/ID for audit.
- Never invent a historical incident.

## Better-than-basic RAG ideas

### Hybrid retrieval
Combine semantic similarity with exact error tokens such as `401`, `ECONNREFUSED`, service name, exception class or stack-trace function.

### Metadata filtering
Filter by environment/component/category before broad retrieval when confidence is high.

### Reranking
Use a lightweight cross-encoder or LLM reranker only if latency remains acceptable.

### Evidence diversity
Avoid returning five nearly identical runbook chunks. Prefer evidence from different useful sources.

## Structured incident memory

After an incident is resolved, store the verified outcome rather than the entire conversation dump.

High-value memory:
- symptom signature;
- actual root cause;
- action that succeeded;
- action that failed;
- environment;
- verification result;
- recurrence indicators.

Low-value memory:
- verbose reasoning text;
- unsupported hypotheses;
- temporary chat filler.

## Evaluation

Measure:
- Hit@1 / Hit@K for known incidents;
- relevance of retrieved fix;
- no-match behavior for novel incidents;
- category-filter errors;
- latency;
- whether retrieval improves RCA over LLM-only baseline.

## Demo cases

At minimum include:
- clear exact-ish historical match;
- paraphrased semantic match;
- misleading near-match;
- no known match;
- same symptom but different environment/root cause.

## Finalization after PS

Freeze:
- actual corpus;
- embedding model;
- index type;
- metadata schema;
- threshold;
- Top-K;
- reranking policy;
- how knowledge is updated during demo.
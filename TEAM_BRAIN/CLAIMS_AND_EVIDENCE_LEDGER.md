# CLAIMS AND EVIDENCE LEDGER

Last updated: 2026-09-11

Purpose: prevent the team from making unsupported claims in README, PPT, demos, forms or judge Q&A.

## Claim status labels

- **FACT** — directly supported by organizer information, code, benchmark result, or cited first-party source.
- **MEASURED** — produced by our own reproducible test/evaluation.
- **INFERENCE** — reasonable conclusion from facts but not directly measured.
- **HYPOTHESIS** — product/research idea requiring validation.
- **FUTURE SCOPE** — planned, not currently implemented.
- **DO NOT CLAIM** — unsupported/misleading.

## Current project claims

| Claim | Status | Evidence / source | Usage rule |
|---|---|---|---|
| Kurukshetra 2.0 is a 24-hour offline hackathon on 11–12 Sep 2026 | FACT | `EVENT_AND_CONSTRAINTS.md` | Safe to state |
| Our team has four members | FACT | team setup / repo branches | Safe to state |
| Current project direction is agentic engineering incident response | FACT about current direction | `CANONICAL_PROJECT_DESCRIPTION.md` | Say “current direction/proposed project” until PS frozen |
| Mature products already use AI for incident investigation | FACT | `SOURCES.md`, `RESEARCH_LEDGER.md` | Safe with citation/context |
| Basic bug routing + RAG + email is not unique | INFERENCE | competitor/reference analysis | Safe as internal strategy; phrase carefully publicly |
| Evidence-backed multi-hypothesis RCA could differentiate us | HYPOTHESIS | `PRODUCT_STRATEGY.md` | Do not claim market uniqueness without validation |
| Risk-aware approval improves safety | HYPOTHESIS supported by industry patterns | `SECURITY_AND_GUARDRAILS.md`, `SOURCES.md` | Present as design principle, not proven outcome yet |
| Incident memory can reduce repeated investigation | HYPOTHESIS | `PRODUCT_STRATEGY.md` | Validate with demo/benchmark/user evidence |
| System reduces incident resolution time by X% | DO NOT CLAIM YET | no measured result | Only after reproducible benchmark |
| System has X% RCA accuracy | DO NOT CLAIM YET | no evaluation result | Measure first |
| System is production-ready | DO NOT CLAIM | hackathon prototype | Never say unless future evidence supports |
| System autonomously fixes production incidents | DO NOT CLAIM | intentionally blocked by safety model | Say recommendation/approved bounded action only |
| We trained our own AI model | DO NOT CLAIM unless true later | current design uses pretrained models/RAG | Say “uses pretrained LLM/embedding model” |
| Project is first/unique in the world | DO NOT CLAIM | competitors exist | Use specific differentiated workflow claim instead |
| Project is patentable | DO NOT CLAIM | no legal novelty analysis | Future possibility only after proper search |
| Demo mode equals live production integration | DO NOT CLAIM | demo fixtures | Label demo mode honestly |

## How to add measured claims

For every measured claim add:

```text
Claim:
Metric:
Dataset / fixture set:
Sample size:
Model/config version:
Date:
Command/test procedure:
Raw result location:
Limitations:
```

## Examples of acceptable future measured claims

If actually measured:
- “On our 20-case benchmark, routing accuracy was 90%.”
- “RAG returned the correct historical incident in Top-3 for 17/20 fixtures.”
- “Median time from submission to remediation recommendation was 6.2 seconds in demo mode.”
- “All 10 high-risk action fixtures were blocked from automatic execution.”

Always include benchmark size/context when judges ask.

## Claims review before submission

Before final README/PPT:
1. search for percentages and superlatives;
2. verify every number against this ledger;
3. remove “100%”, “guaranteed”, “first”, “best”, “production-ready” unless truly defensible;
4. clearly mark future scope;
5. ensure competitor comparisons reflect current sources;
6. ensure screenshots/demo states correspond to implemented code.
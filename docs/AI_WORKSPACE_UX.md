# AI Workspace UX — final hackathon product direction

This document records the judge-facing UX direction for the AI Agentic Bug Router. It is intentionally implementation-oriented: every prominent action should map to a real backend capability, a truthful fallback, or an explicitly unavailable state.

## Product idea in one screen

The home surface is now the **AI Workspace**. A user should not need to understand the internal tab structure before starting. They can describe a software failure in natural language, optionally attach bounded source/test files, optionally point the agent at the allowlisted GitHub repository, select the environment, and start an evidence-first investigation.

The workspace then routes into the existing real capabilities rather than replacing them:

```text
bug description
+ optional source/test files
+ optional allowlisted GitHub repository
        |
        +--> isolated uploaded-file investigation
        |      -> RAG
        |      -> Qwen when live
        |      -> exact patch preview
        |      -> reviewed isolated edit
        |      -> trusted pytest or static validation
        |
        +--> persisted incident investigation
               -> triage / owner routing
               -> historical evidence
               -> live GitHub commits / issues / diffs
               -> RCA hypothesis
               -> Evidence Lab
               -> human-gated Remediation Studio
               -> isolated fix branch
               -> deterministic validation
               -> Draft PR
               -> real CI evidence
```

The older specialized screens remain available because they are useful proof surfaces for technical judges. The workspace is the entry point; the specialist screens expose the engineering depth.

## Visual direction

The design follows a restrained, platform-like hierarchy rather than turning every card into glass.

- **Light-first neutral canvas** with high-legibility typography and large negative space.
- **Liquid-glass treatment only for navigation and important interactive/control surfaces**, such as the global sidebar, AI composer and floating theme control.
- **Mostly opaque content cards** for code, evidence, results and evaluation so information remains easy to scan.
- **Subtle depth**, not gaming-style 3D: soft aurora layers, floating depth planes and pointer/scroll parallax behind the main workspace.
- **Small radii + capsule controls** where they convey grouping; large cards use consistent 18–28 px radii.
- **System font stack** for a native/product feel without shipping custom fonts.
- **Dark mode remains first-class** with the same hierarchy rather than simply inverting colors.
- **Motion communicates state**. It should not become decoration that competes with evidence.

The implementation also honors `prefers-reduced-motion` and `prefers-reduced-transparency` so the visual system does not depend on animation or blur to remain understandable.

## Main composer

The main composer intentionally resembles modern AI workspaces while staying engineering-specific.

It supports:

- freeform bug/error description;
- expected vs observed behavior in the same prompt;
- GitHub `owner/repository` attachment;
- production/staging/development environment selection;
- drag/drop or file-picker attachment for allowlisted text/code formats;
- explicit **Trusted tests** opt-in for uploaded Python tests;
- visible GitHub, RAG and model context;
- one clear investigate action.

The user is never asked to paste a GitHub token into the composer.

## Source and connector policy

Only functional sources are shown as active product capabilities today:

- uploaded files;
- allowlisted GitHub repository evidence;
- local curated RAG / verified-resolution knowledge;
- local Qwen/Ollama or the configured truthful model fallback.

Future connectors such as issue trackers, Slack or cloud file providers can use the same source-chip pattern, but they must not appear as connected until a real backend connector and permission model exists.

## Loading / shimmer policy

Long operations must visibly explain that work is still happening without inventing partial results.

Current loading system:

- reusable neutral skeleton shimmer for first-load and multi-card evidence operations;
- a thin global operation shimmer whenever an existing screen is performing a spinner-backed network/model/GitHub action;
- explicit action text such as `Investigating evidence, not guessing...`, `Qwen reasoning...`, `Applying + verifying...`;
- buttons disable while the same operation is in flight to reduce accidental duplicates.

Skeletons are placeholders only; they never contain fake metric values or fabricated benchmark results.

## Truthful live-state labels

The product distinguishes these states rather than collapsing them into one green indicator:

- `LIVE_FIRST` — real integrations are preferred;
- `FALLBACK_DEMO` — explicitly configured fallback/demo mode;
- local model installed/reachable;
- **live model inference actually probed**;
- GitHub public/authenticated read access;
- **GitHub push permission actively verified**;
- no-check / pending / fail / pass CI states.

A configured environment variable alone is not proof that a model or GitHub write path works.

## Ollama/Qwen reliability

The local-model path supports both Ollama interfaces:

- OpenAI-compatible `/v1/models` and `/v1/chat/completions`;
- native `/api/tags` and `/api/chat` fallback.

`setup-local-ai.bat` now waits for the service, ensures `qwen3:4b` is installed and performs a real native inference warm-up before printing success.

The Readiness page can perform another real inference probe from the backend so the demo proves the application itself can call Qwen.

## GitHub write reliability

Read-only repository investigation remains separate from write authority.

The Readiness page can perform a **read-only GitHub permission probe** for the configured allowlisted repository and report:

- credential source (`GH_CLI`, local environment token, or none) without returning the credential;
- repository allowlist result;
- authenticated state;
- whether GitHub reports `push` permission.

If write permission is unavailable, the UI explains how to verify/login with GitHub CLI rather than waiting for a remediation action to fail late.

The actual remediation contract remains unchanged:

```text
exact reviewed proposal
-> explicit human APPROVE
-> fresh state/stale check
-> isolated incident-fix branch
-> exact approved replacement
-> deterministic validation
-> Draft PR only when validation succeeds
```

There is intentionally **no automatic merge** and no production deployment. The final Draft PR is a handoff to the normal human GitHub review/merge process.

## Specialist proof surfaces

- `/` or `/workspace` — conversational AI Workspace.
- `/incidents` — Incident Command lifecycle and audit timeline.
- `/prototype` — strongest deterministic real-file FAIL -> PASS proof.
- `/intake` — dedicated judge-supplied files + Qwen proof workflow.
- `/demo` — controlled golden judge flow.
- `/ai` — RAG / repository evidence / RCA reasoning explanation.
- `/evidence` — live read-only GitHub commit, diff-hunk and source-context proof.
- `/remediate` — exact approval-gated live GitHub branch / validation / Draft PR workflow.
- `/evaluation` — measured deterministic benchmark scorecard.
- `/readiness` — active runtime, Qwen and GitHub permission truth surface.

## Final UX rule

The interface should feel calm even when the incident is serious. Evidence, decisions and safety state matter more than visual novelty. Parallax, blur and animation are there to create hierarchy and polish; they must never hide a failed validator, a fallback label, a missing GitHub permission or a human approval boundary.

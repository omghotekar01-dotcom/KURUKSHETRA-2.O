# Real-Use Audit — AI Agentic Bug Router

Date: **11 September 2026**  
Purpose: verify that the project is useful as an actual bounded engineering workflow, not only visually convincing in a hackathon demo.

## Verdict

**The supported hackathon workflow is real-use functional for its declared scope.**

It can accept realistic software incidents, route them to a technical area, optionally map those areas to real organization team names, investigate an allowlisted GitHub repository, use stack-trace/file-path clues to prioritize changed code, surface repository ownership hints from CODEOWNERS, combine repository evidence with verified historical knowledge, prepare only sufficiently grounded exact patch candidates, require explicit human approval, validate supported changes on an isolated branch, create a Draft PR only after green checks, read real GitHub CI state afterward, and derive canonical verification evidence from the exact remediation commit/check state.

This is deliberately a **bounded incident-response assistant**, not a universal autonomous bug fixer. It does not claim to synthesize the correct semantic fix for every programming language or incident.

## Real-use gaps found and fixed

### 1. Stack traces now materially influence code ranking

Before the audit, repository ranking was mainly lexical. A realistic trace such as:

```text
File "C:\service\backend\payments\charge.py", line 87
ValueError: invalid provider amount
```

could lose signal because file-system punctuation diluted the keyword overlap.

The repository evidence layer now extracts code paths from incident text/logs and gives explainable ranking weight to exact/suffix/basename path matches. A matching changed file therefore ranks substantially above an unrelated documentation change while still being labeled correlation, not causation.

### 2. Weakly related code can no longer become a patch just because exact lines exist

Patch proposal generation now enforces `PATCH_PROPOSAL_MIN_CORRELATION` (default `0.18`).

If a diff hunk is below that threshold, the system returns a fail-closed response asking for stronger evidence/manual investigation. No repository write occurs.

### 3. Unsupported operational/configuration changes fail closed

The validation gate no longer treats arbitrary file types as safe text changes.

Supported deterministic paths include:

- frontend TypeScript/JavaScript → locked `npm ci` + production build;
- backend Python → compile + pytest;
- explicit documentation text (`.md`, `.txt`, `.rst`) → exact branch content-integrity verification.

Configuration/automation/unsupported executable types such as GitHub Actions YAML, Terraform, Dockerfile, shell/PowerShell scripts and unknown file types are blocked from automatic Draft PR creation unless a trusted validator is added.

### 4. Frontend validation is reproducible

Remediation validation now uses the committed npm lockfile with:

```text
npm ci --no-audit --no-fund
npm run build
```

rather than allowing dependency resolution to drift during a fix validation.

### 5. Real organization routing no longer requires code edits

`TRIAGE_OWNER_MAP` lets an operator map deterministic components to actual team names:

```env
TRIAGE_OWNER_MAP=Authentication=identity-platform,Database=data-reliability,Backend=api-platform,Frontend=web-experience,Infrastructure=sre
```

The built-in team names remain safe defaults when no mapping is supplied.

### 6. Repository CODEOWNERS contributes routing/review hints

When the investigated repository contains CODEOWNERS in a supported standard location, the live evidence layer reads it from the repository default branch and resolves owner candidates for the highest-ranked changed files.

These owner candidates are surfaced as **routing/review suggestions only**. They do not grant authorization and do not override the approval safety boundary.

Supported lookup locations:

```text
.github/CODEOWNERS
CODEOWNERS
docs/CODEOWNERS
```

The configured component-to-team mapping remains the fallback when no matching CODEOWNERS rule exists.

### 7. CI verification is now incident evidence, not just a badge

The CI verification endpoint records canonical evidence tied to the exact repository, remediation commit, Draft PR and observed checks.

- Real CI `FAIL` derives a failed incident-verification outcome and escalates.
- `PENDING` / `NO_CHECKS` produces inconclusive evidence instead of success.
- CI `PASS` is kept as strong evidence but does **not** auto-resolve the original incident; runtime/human verification is still required.

This makes the workflow useful operationally because CI state becomes auditable incident evidence without pretending that green tests prove production recovery.

## Realistic regression scenarios

The automated suite now includes realistic incident language rather than only idealized fixture phrases:

| Scenario | Expected behavior |
|---|---|
| JWT signature failures after login | Authentication routing |
| Postgres connection-pool exhaustion | Database routing |
| 502/worker/upstream failure | Backend routing |
| React/CSS mobile overlap | Frontend routing |
| Kubernetes CrashLoop/OOM | Infrastructure routing |
| Unknown subsystem with weak evidence | human/no-match path rather than invented certainty |
| Stack trace naming a changed source file | matching source path receives strong ranking boost |
| Exact code hunk with only 5% incident correlation | patch proposal blocked |
| Workflow YAML / Terraform / Dockerfile remediation | automatic Draft PR blocked without trusted validator |
| Duplicate exact approval | existing remediation state reused rather than duplicated |
| Missing GitHub auth for a write | explicit `AUTH_REQUIRED`; no fake success |
| No CI checks | `NO_CHECKS`; never converted into PASS |
| CI failure | incident verification derives FAIL and escalates |
| CI pass | retained as evidence; runtime verification still required |

## Latest audited executable proof point

Executable code head:

`18112b436803f747a23d60bf5ce73c952f9523a7`

GitHub Actions:

- run **#409**
- run ID `34597412643`

Confirmed results:

```text
Backend compile:                       PASS
Backend tests:                         73 passed, 0 failures
Frontend locked install:               PASS
Frontend TypeScript/Vite build:        PASS
Windows launcher syntax:               PASS
Windows strict environment preflight:  PASS
Windows clean bootstrap:               PASS
Release candidate contract:            PASS
Clean-clone acceptance:                4/4 PASS
Release-candidate acceptance:          PASS
```

The Windows job performs a fresh checkout/bootstrap before acceptance, so the proof is not dependent on a developer's existing local `node_modules` or Python environment.

## What “actually useful” means for this release

A developer can use the product to reduce manual incident investigation by putting these steps in one auditable workflow:

```text
bug report + logs + repo
→ component/team triage
→ historical incident/runbook lookup
→ live commits/files/diffs/source context
→ stack-trace/path correlation
→ CODEOWNERS routing/review hints
→ RCA candidate + next diagnostic
→ exact safety-gated patch candidate when evidence is strong enough
→ human approval
→ isolated branch
→ deterministic validation
→ Draft PR
→ real CI verification
→ derived verification evidence
→ human runtime verification
→ verified-resolution memory
```

The useful behavior is not merely that it produces an answer. The system also knows when **not** to act: weak evidence, stale source, ambiguous replacement, unsupported validator, missing auth, conflicting retry state and absent CI checks all stop or escalate instead of being presented as success.

## Truth boundaries

This release does **not** claim:

- universal root-cause accuracy;
- proof that a correlated commit caused the incident;
- automatic semantic code repair for every defect;
- automatic merge or production deployment;
- production recovery merely because CI is green;
- a trained custom ML model;
- complete CODEOWNERS grammar compatibility for every exotic pattern/escaping edge case;
- complete DLP or universal prompt-injection prevention;
- enterprise multi-region/distributed-locking readiness.

Those limits are intentional. For this hackathon MVP, the safer and more useful behavior is to expose evidence, make bounded changes only when supported, and fail closed otherwise.

## Final operator check on the hackathon laptop

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\HACKATHON\KURUKSHETRA-2.O
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Then test one normal realistic incident in `/`, one live repository investigation in `/evidence`, the controlled flow in `/demo`, and `/evaluation` + `/readiness` before judging.

For live remediation writes, authenticate locally with GitHub CLI or a local environment token. Never paste a token into the repository, screenshots or chat.

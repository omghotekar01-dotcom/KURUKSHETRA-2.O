# Real-Use Audit — AI Agentic Bug Router

Date: **11 September 2026**  
Purpose: verify that the project is useful as an actual bounded engineering workflow, not only visually convincing in a hackathon demo.

## Verdict

**The supported hackathon workflow is real-use functional for its declared scope.**

It can accept realistic software incidents, route them to a technical area, optionally map those areas to real organization team names, investigate an allowlisted GitHub repository, use stack-trace/file-path clues to prioritize changed code, surface repository ownership hints from CODEOWNERS, combine repository evidence with verified historical knowledge, prepare only sufficiently grounded exact patch candidates, require explicit human approval, validate supported changes on an isolated branch, create a Draft PR only after green checks, read real GitHub CI state afterward, and derive canonical verification evidence from the exact remediation commit/check state.

This is deliberately a **bounded incident-response assistant**, not a universal autonomous bug fixer. It does not claim to synthesize the correct semantic fix for every programming language or incident.

## Real-use gaps found and fixed

### 1. Stack traces materially influence code ranking

A realistic trace such as:

```text
File "C:\service\backend\payments\charge.py", line 87
ValueError: invalid provider amount
```

is now parsed for file-path evidence. Exact/suffix/basename matches receive explainable ranking weight so the named changed source file can outrank unrelated repository noise. This remains correlation, not causal proof.

### 2. Weakly related code cannot become a patch just because exact lines exist

Patch proposal generation enforces `PATCH_PROPOSAL_MIN_CORRELATION` (default `0.18`). A hunk below that threshold fails closed and asks for stronger evidence/manual investigation. No repository write occurs.

### 3. Unsupported operational/configuration changes fail closed

Supported deterministic validation paths include:

- frontend TypeScript/JavaScript → locked `npm ci` + production build;
- backend Python → compile + pytest;
- explicit documentation text (`.md`, `.txt`, `.rst`) → exact branch content-integrity verification.

Configuration/automation/unsupported executable types such as GitHub Actions YAML, Terraform, Dockerfile, shell/PowerShell scripts and unknown file types are blocked from automatic Draft PR creation unless a trusted validator is added.

### 4. Frontend validation is reproducible

Remediation validation uses the committed npm lockfile:

```text
npm ci --no-audit --no-fund
npm run build
```

rather than allowing dependency resolution to drift during a fix validation.

### 5. Real organization routing does not require code edits

`TRIAGE_OWNER_MAP` can map deterministic components to actual team names:

```env
TRIAGE_OWNER_MAP=Authentication=identity-platform,Database=data-reliability,Backend=api-platform,Frontend=web-experience,Infrastructure=sre
```

Built-in owners remain fallbacks when no mapping is supplied.

### 6. Repository CODEOWNERS contributes routing/review hints

When present in a supported standard location, CODEOWNERS is read from the repository default branch and owner candidates are resolved for the highest-ranked changed files.

Supported lookup locations:

```text
.github/CODEOWNERS
CODEOWNERS
docs/CODEOWNERS
```

These are **routing/review suggestions only**. They do not grant authorization and do not override the human approval boundary.

### 7. CI verification is incident evidence, not just a badge

The CI verification endpoint records canonical evidence tied to the exact repository, remediation commit, Draft PR and observed checks.

- CI `FAIL` derives failed incident verification and escalates.
- `PENDING` / `NO_CHECKS` is inconclusive rather than success.
- CI `PASS` remains evidence and still requires runtime/human verification; it cannot auto-resolve the original incident.

## Realistic regression scenarios

The suite includes realistic incident language rather than only idealized fixtures:

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
| CI failure | derives failed incident verification and escalates |
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

The Windows job performs a fresh checkout/bootstrap before acceptance, so this proof is not dependent on a developer's existing local `node_modules` or Python environment. Subsequent closure commits are documentation-only.

## What “actually useful” means for this release

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

The useful behavior is not merely that it produces an answer. It also knows when **not** to act: weak evidence, stale source, ambiguous replacement, unsupported validator, missing auth, conflicting retry state and absent CI checks all stop or escalate instead of being presented as success.

## Truth boundaries

This release does **not** claim universal root-cause accuracy, causal proof from commit correlation, automatic semantic code repair for every defect, automatic merge/deployment, production recovery merely because CI is green, a trained custom ML model, complete CODEOWNERS grammar compatibility, complete DLP/universal prompt-injection prevention, or enterprise distributed-locking readiness.

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

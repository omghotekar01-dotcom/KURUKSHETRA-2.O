# Real-Use Audit — AI Agentic Bug Router

Date: **11 September 2026**  
Purpose: verify that the project is useful as an actual bounded engineering workflow, not only visually convincing in a hackathon demo.

## Verdict

**The supported hackathon workflow is real-use functional for its declared scope.**

It accepts realistic software incidents, routes them to a technical area, can map those areas to real organization team names, investigates an allowlisted GitHub repository, uses stack-trace/file-path clues to prioritize changed code, surfaces CODEOWNERS routing/review hints, combines repository evidence with verified historical knowledge, prepares only sufficiently grounded exact patch candidates, requires explicit human approval, validates supported changes on an isolated branch, creates a Draft PR only after green checks, reads real GitHub CI state and records derived verification evidence.

It is deliberately a **bounded incident-response assistant**, not a universal autonomous bug fixer.

## Real-use hardening completed

- Stack-trace/file-path clues materially influence changed-code ranking.
- `PATCH_PROPOSAL_MIN_CORRELATION` (default `0.18`) blocks weak patch candidates.
- Frontend remediation uses locked `npm ci` + production build.
- Backend Python remediation uses compile + pytest.
- Unknown/configuration/operational file types fail closed without a trusted validator.
- `TRIAGE_OWNER_MAP` maps components to real organization teams without code edits.
- Repository CODEOWNERS provides advisory review/routing hints when available.
- Duplicate exact approvals reuse existing remediation state.
- Missing GitHub auth surfaces `AUTH_REQUIRED` rather than fake success.
- CI `FAIL` derives failed incident verification and escalates.
- CI `PENDING` / `NO_CHECKS` remains inconclusive.
- CI `PASS` is evidence only and still requires runtime/human verification.

## Realistic regression scenarios

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

Executable code head: `18112b436803f747a23d60bf5ce73c952f9523a7`  
GitHub Actions: **run #409**, run ID `34597412643`

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

The Windows job performs a fresh checkout/bootstrap before acceptance, so this proof is not dependent on an existing local environment. Subsequent closure commits are documentation-only.

## Actual supported workflow

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

The useful behavior is not merely that it produces an answer. It knows when **not** to act: weak evidence, stale source, ambiguous replacement, unsupported validator, missing auth, conflicting retry state and absent CI checks stop or escalate instead of being presented as success.

## Truth boundaries

This release does **not** claim universal root-cause accuracy, causal proof from commit correlation, automatic semantic code repair for every defect, automatic merge/deployment, production recovery merely because CI is green, a trained custom ML model, complete CODEOWNERS grammar compatibility, complete DLP/universal prompt-injection prevention, or enterprise distributed-locking readiness.

Those limits are intentional: expose evidence, make bounded changes only when supported, and fail closed otherwise.

## Final operator check

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\HACKATHON\KURUKSHETRA-2.O
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Then test one realistic incident in `/`, live repository investigation in `/evidence`, the controlled flow in `/demo`, and `/evaluation` + `/readiness` before judging. For live remediation writes, authenticate locally; never paste a token into the repository, screenshots or chat.

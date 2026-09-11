# Real-Use Audit — AI Agentic Bug Router

Date: **11 September 2026**

**Verdict: the supported hackathon workflow is real-use functional for its declared scope.**

The project was audited for actual engineering usefulness rather than only demo behavior. It now supports realistic incident triage, configurable organization ownership, live GitHub evidence, stack-trace/file-path correlation, CODEOWNERS routing hints, evidence-backed RCA, safety-thresholded exact patch proposals, approval-gated isolated remediation, trusted validation, Draft PR creation, real CI verification, derived verification evidence and human runtime verification.

## Hardening completed

- Stack-trace/file-path clues influence changed-code ranking.
- `PATCH_PROPOSAL_MIN_CORRELATION` blocks weak patch candidates (default `0.18`).
- Frontend remediation uses locked `npm ci` + production build.
- Backend Python remediation uses compile + pytest.
- Unknown/configuration/operational file types fail closed without a trusted validator.
- `TRIAGE_OWNER_MAP` maps components to real teams without code edits.
- CODEOWNERS can provide advisory review/routing hints.
- Duplicate exact approvals reuse existing remediation state.
- Missing GitHub auth returns `AUTH_REQUIRED`, not fake success.
- CI `FAIL` derives failed verification and escalates.
- CI `PENDING` / `NO_CHECKS` stays inconclusive.
- CI `PASS` remains evidence and still requires runtime/human verification.

## Latest audited executable proof

Executable head: `18112b436803f747a23d60bf5ce73c952f9523a7`  
GitHub Actions: **run #409**, ID `34597412643`

```text
Backend compile:                       PASS
Backend tests:                         73 passed, 0 failures
Frontend locked install/build:         PASS
Windows launcher syntax:               PASS
Windows strict environment preflight:  PASS
Windows clean bootstrap:               PASS
Release candidate contract:            PASS
Clean-clone acceptance:                4/4 PASS
Release-candidate acceptance:          PASS
```

The Windows job performs a fresh checkout/bootstrap before acceptance. Subsequent closure commits are documentation-only.

## Actual supported workflow

```text
bug report + logs + repo
→ component / real-team triage
→ historical incident/runbook lookup
→ live GitHub commits/files/diffs/source
→ stack-trace/path correlation
→ CODEOWNERS review/routing hints
→ RCA candidate + next diagnostic
→ safety-gated exact patch candidate
→ human approval
→ isolated branch
→ deterministic trusted validation
→ Draft PR
→ real CI verification
→ derived verification evidence
→ human runtime verification
→ verified-resolution memory
```

The system also knows when **not** to act: weak evidence, stale source, ambiguous replacement, unsupported validator, missing auth, conflicting retry state and absent CI checks stop or escalate instead of being shown as success.

## Truth boundary

This is a bounded incident-response MVP, not a universal autonomous bug fixer. It does not claim universal RCA accuracy, causal proof from commit correlation, semantic repair for every defect/language, automatic merge/deployment, production recovery from green CI alone, complete DLP/prompt-injection prevention, or enterprise distributed-locking readiness.

## Final laptop check

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\HACKATHON\KURUKSHETRA-2.O
git switch agent-build-core
git pull --ff-only origin agent-build-core
.\verify.bat
.\start.bat
```

Then exercise one realistic incident in `/`, live evidence in `/evidence`, Judge Mode `/demo`, `/evaluation`, and `/readiness`. Authenticate GitHub locally only if demonstrating a real remediation write.
